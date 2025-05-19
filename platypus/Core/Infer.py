import platypus.Utils.Foundation as Foundation

class Infer(object):

    def __init__(self,
                 _Query : str,
                 _ModelName : str = Foundation.PLATYPUS_DEFAULT_LANGUAGE_MODEL,
                 _CacheDir : str = "Platypus_Cache", **kwargs):

        # Initialize Model & Tokenizer
        self.__Model        = Foundation.AutoModelForCausalLM.from_pretrained(_ModelName, cache_dir = _CacheDir)
        self.__Tokenizer    = Foundation.AutoTokenizer.from_pretrained(_ModelName, cache_dir = _CacheDir)
        self.ModelName      = _ModelName
        self.Query          = _Query

        # System Role Prompt
        self.__SystemRole = \
        """
        You are an Smart Research Paper Analyzer, Your
        Task is to Analyze the Keywords in this Research
        Paper then Formulate the best possible Query
        that articulates the overall interest of the research
        paper. The Query should be suitable for passing directly
        into REST API like Arxiv, ResearchGate etc.            
        """
        # Prompt Template from Google
        self.Prompt = [
            {
                "role"      : "system",
                "content"   : self.__SystemRole
            },
            {
                "role"      : "user", 
                "content"   : self.Query
            }
        ]

        chat_formatted_prompt = self.__Tokenizer.apply_chat_template(
            self.Prompt,
            tokenize=False,
            add_generation_prompt=True
        )

        # 2. Tokenize the formatted prompt
        inputs = self.__Tokenizer(chat_formatted_prompt, return_tensors="pt")

        # 3. Generate the response using the model's generate method
        #    Add generation parameters here
        output_tokens = self.__Model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"], # Important for batched generation if you were doing it
            max_new_tokens=64,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=0.7,
            pad_token_id=self.__Tokenizer.eos_token_id # Use eos_token as pad_token_id
        )

        # 4. Decode the generated tokens
        #    Decode the whole output, then potentially strip the input prompt part
        #    Or decode starting from the first generated token index if needed
        #    For chat models, decoding the *entire* sequence and then slicing is often easier
        decoded_output = self.__Tokenizer.decode(output_tokens[0], skip_special_tokens=True)

        # The decoded_output contains the original prompt + the generated text.
        # We need to extract only the generated response part.
        # A simple way is to find where the assistant turn started in the original formatted prompt
        # and take everything after that point in the decoded output.
        # This requires knowing the exact structure added by apply_chat_template.
        # A more robust way is to decode the generated tokens *after* the input length.

        # Let's re-generate and decode just the new tokens
        output_tokens_only_new = self.__Model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_new_tokens=1024,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            temperature=0.7,
            pad_token_id=self.__Tokenizer.eos_token_id # Use eos_token as pad_token_id
        )

        # The output_tokens_only_new tensor includes the input tokens.
        # To get *only* the generated part, we need to decode from the token index
        # that corresponds to the start of the generated text.
        # This index is simply the length of the input tokens.
        input_length = inputs["input_ids"].shape[1]
        generated_tokens = output_tokens_only_new[:, input_length:]

        # Decode *only* the generated tokens
        self.InferredText = self.__Tokenizer.decode(generated_tokens[0], skip_special_tokens=True)

        # --- End of Manual Generation ---
       