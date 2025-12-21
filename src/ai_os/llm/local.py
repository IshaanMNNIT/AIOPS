from llama_cpp import Llama

class LocalLLMClient:
    def __init__(self , model_path : str):
        self.llm = Llama(
            model_path=model_path,
            n_ctx=2048,
            n_threads=8,
            verbose=False
        )
    
    def generate(self, prompt:str) -> str:
        output = self.llm(
            prompt,
            max_tokens=512,
            temperature=0.0,
            top_p=1.0,
            stop=["\n\n", "</s>"],
        )

        return output["choices"][0]["text"].strip()


