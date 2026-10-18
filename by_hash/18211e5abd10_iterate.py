"""
Molt Iterator - Recursive improvement engine
"""

from typing import List, Dict, Optional, Tuple # Added Tuple
from pathlib import Path

class MoltIterator:
    def __init__(self, ollama_client):
        self.ollama = ollama_client
        self.system_prompt = self._load_system_prompt()
        
    def _load_system_prompt(self) -> str:
        """Load the base molt system prompt"""
        # Path adjusted for the new src structure: src/core/iterate.py -> src/prompts/system.txt
        prompt_path = Path(__file__).parent.parent.parent / 'prompts' / 'system.txt' # Corrected path
        if prompt_path.exists():
            return prompt_path.read_text()
        return self._default_system_prompt()
    
    def _default_system_prompt(self) -> str:
        return """You are MOLT - a recursive self-improvement system.
Your job is to take a task and improve upon previous attempts.

Rules:
1. Analyze what came before
2. Identify weaknesses
3. Generate a better version
4. Be concise but complete
5. Focus on practical improvements

You are part of a growth process. Each iteration should be measurably better."""
    
    def iterate(self, task: str, previous_results: List[Dict]) -> Dict:
        """Run one iteration of improvement"""
        
        # Build context from previous attempts
        context = self._build_context(task, previous_results)
        
        # Generate improved version
        prompt = self._build_prompt(task, context)
        
        # Call OllamaClient.generate, which now returns (response_text, error_message)
        response_text, error_message = self.ollama.generate(prompt, system=self.system_prompt)
        
        if error_message:
            return {
                'output': f"Error during Ollama generation: {error_message}",
                'score': 0.0,
                'is_improvement': False,
                'iteration': len(previous_results) + 1,
                'error': error_message # Propagate the error message
            }
        
        output = response_text
        
        # Evaluate the result
        score = self._evaluate(output, previous_results)
        is_improvement = len(previous_results) == 0 or score > max(
            r.get('score', 0) for r in previous_results
        )
        
        return {
            'output': output,
            'score': score,
            'is_improvement': is_improvement,
            'iteration': len(previous_results) + 1
        }
    
    def _build_context(self, task: str, previous_results: List[Dict]) -> str:
        """Build context string from previous attempts"""
        if not previous_results:
            return "This is the first attempt."
        
        context = f"Previous attempts ({len(previous_results)}):\n\n"
        for i, result in enumerate(previous_results[-3:], 1):  # Last 3 only
            # Ensure 'output' key exists and is not an error message
            output_content = result.get('output', 'No output').split("Error during Ollama generation:")[0] # Strip error msg
            context += f"Attempt {i} (score: {result.get('score', 0):.2f}):\n"
            context += output_content[:200] + "...\n\n"
        
        return context
    
    def _build_prompt(self, task: str, context: str) -> str:
        """Build the improvement prompt"""
        return f"""Task: {task}

{context}

Now generate an improved version. Consider:
- What worked in previous attempts?
- What can be enhanced?
- How can this be more effective?

Your improved version:"""
    
    def _evaluate(self, output: str, previous_results: List[Dict]) -> float:
        """Simple evaluation - can be enhanced later"""
        # If output is an error message, score it very low
        if output.startswith("Error during Ollama generation:"):
            return -1.0 # Very low score for errors
        
        score = 0.0
        
        # Length (not too short, not too long)
        length = len(output)
        if 50 < length < 2000:
            score += 0.3
        
        # Structure (has newlines, sections)
        if '\n' in output:
            score += 0.2
        
        # Different from previous (novelty)
        if previous_results:
            last_output = previous_results[-1].get('output', '')
            # Only compare if last_output is not an error
            if not last_output.startswith("Error during Ollama generation:"):
                similarity = self._simple_similarity(output, last_output)
                score += (1 - similarity) * 0.3
        
        # Completeness (doesn't end abruptly)
        if output.strip().endswith(('.', '!', '?', '```')):
            score += 0.2
        
        return min(score, 1.0) # Ensure score doesn't exceed 1.0
    
    def _simple_similarity(self, text1: str, text2: str) -> float:
        """Quick similarity check"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if not words1 or not words2:
            return 0.0
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union if union > 0 else 0.0
