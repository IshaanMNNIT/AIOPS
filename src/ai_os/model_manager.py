import os
import yaml
import logging
import onnxruntime as ort
from transformers import AutoTokenizer
from config.settings import settings

logger = logging.getLogger(__name__)


class ModelManager:
    def __init__(self, registry_path="config/model_registry.yaml"):
        self.registry_path = registry_path
        self.registry = self._load_registry()

        self.sessions = {}
        self.tokenizers = {}

    def _load_registry(self):
        with open(self.registry_path, "r") as f:
            return yaml.safe_load(f)["models"]

    def list_models(self):
        return list(self.registry.keys())

    def _load_model(self, name: str):
        if name in self.sessions:
            return

        if name not in self.registry:
            raise ValueError(f"Model '{name}' not registered")

        cfg = self.registry[name]

        model_path = cfg["path"]
        tokenizer_id = cfg["tokenizer"]
        device = cfg.get("device", settings.default_device)

        if not os.path.exists(model_path):
            raise FileNotFoundError(model_path)

        providers = (
            ["CUDAExecutionProvider", "CPUExecutionProvider"]
            if device == "cuda"
            else ["CPUExecutionProvider"]
        )

        logger.info("Loading model '%s' on %s", name, device)

        session = ort.InferenceSession(model_path, providers=providers)
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_id)

        self.sessions[name] = session
        self.tokenizers[name] = tokenizer

    def infer(self, model: str, text: str):
        self._load_model(model)

        session = self.sessions[model]
        tokenizer = self.tokenizers[model]
        cfg = self.registry[model]

        encoded = tokenizer(
            text,
            return_tensors="np",
            padding="max_length",
            truncation=True,
            max_length=cfg.get("max_length", 32),
        )

        ort_inputs = {}
        for inp in session.get_inputs():
            name = inp.name
            if name == "input_ids":
                ort_inputs[name] = encoded["input_ids"]
            elif name == "attention_mask":
                ort_inputs[name] = encoded["attention_mask"]
            elif name == "token_type_ids":
                # Some models require this even for single-sentence input
                ort_inputs[name] = encoded.get(
                    "token_type_ids",
                    encoded["input_ids"] * 0
                )

        outputs = session.run(None, ort_inputs)
        embedding = outputs[0][0].mean(axis=0)

        return {
            "model": model,
            "dim": int(embedding.shape[0]),
            "sample": embedding[:5].tolist(),
        }
