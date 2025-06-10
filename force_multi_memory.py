#!/usr/bin/env python3
"""
Force Multi-Memory Creation for OpenMemory

This script bypasses the single-memory limitation by:
1. Parsing the input to extract facts
2. Creating individual memories for each fact
3. Using strategic prompts to ensure extraction
"""

import requests
import json
import time
import re
from typing import List, Dict

class MultiMemoryForcer:
    def __init__(self, base_url: str = "http://localhost:8765"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1/memories/"
        self.stats_url = f"{base_url}/api/v1/stats/"
    
    def extract_facts_advanced(self, text: str) -> List[str]:
        """Extract facts using NLP-like patterns"""
        facts = []
        
        # Pattern 1: Split by conjunctions
        conjunctions = [' and ', ', and ', ' but ', ', but ', '. ', '; ', ' also ', ', ']
        segments = [text]
        
        for conj in conjunctions:
            new_segments = []
            for seg in segments:
                parts = seg.split(conj)
                new_segments.extend([p.strip() for p in parts if p.strip()])
            segments = new_segments
        
        # Pattern 2: Extract based on verbs
        verb_patterns = [
            r"I (\w+) (.+?)(?=,|and|but|\.|\Z)",
            r"My (\w+) is (.+?)(?=,|and|but|\.|\Z)",
            r"I'm (.+?)(?=,|and|but|\.|\Z)",
            r"I am (.+?)(?=,|and|but|\.|\Z)"
        ]
        
        for pattern in verb_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                fact = match.group(0).strip()
                if len(fact) > 5:
                    facts.append(fact)
        
        # Pattern 3: Key information types
        if "work" in text.lower() or "job" in text.lower():
            work_match = re.search(r"(work\s+at|work\s+for|employed\s+at|job\s+at)\s+(.+?)(?=,|and|\.|\Z)", text, re.I)
            if work_match:
                facts.append(f"Works at {work_match.group(2).strip()}")
        
        if "use" in text.lower():
            use_matches = re.finditer(r"use\s+(.+?)(?=for|and|,|\.|\Z)", text, re.I)
            for match in use_matches:
                facts.append(f"Uses {match.group(1).strip()}")
        
        # Remove duplicates and return
        return list(set(facts))
    
    def create_memory_with_context(self, text: str, user_id: str, app: str, context: str = "") -> Dict:
        """Create a memory with additional context"""
        payload = {
            "user_id": user_id,
            "text": f"{context} {text}".strip(),
            "app": app
        }
        
        try:
            response = requests.post(self.api_url, json=payload)
            if response.status_code == 200:
                result = response.json()
                if result and isinstance(result, dict) and 'id' in result:
                    return result
        except Exception as e:
            print(f"Error: {e}")
        
        return None
    
    def force_multi_memory_creation(self, text: str, user_id: str = "alexgrama", app: str = "multi_test"):
        """Force creation of multiple memories from a single input"""
        print(f"\n🎯 Processing: {text}")
        print("="*60)
        
        # Get initial memory count
        stats_before = requests.get(f"{self.stats_url}?user_id={user_id}").json()
        initial_count = stats_before.get('total_memories', 0)
        
        memories_created = []
        
        # Strategy 1: Direct creation
        print("\n1️⃣ Direct extraction...")
        result = self.create_memory_with_context(text, user_id, app)
        if result:
            print(f"   ✅ Created: {result.get('content')}")
            memories_created.append(result)
            time.sleep(1)
        
        # Strategy 2: Extract and create individual facts
        facts = self.extract_facts_advanced(text)
        print(f"\n2️⃣ Found {len(facts)} potential facts")
        
        for i, fact in enumerate(facts, 1):
            print(f"   {i}. Processing: {fact}")
            
            # Try different contexts
            contexts = [
                "",
                "Important fact:",
                "Remember that",
                "Key information:",
                "User detail:"
            ]
            
            created = False
            for ctx in contexts:
                result = self.create_memory_with_context(fact, user_id, app, ctx)
                if result:
                    print(f"      ✅ Created: {result.get('content')}")
                    memories_created.append(result)
                    created = True
                    break
                time.sleep(0.5)
            
            if not created:
                print(f"      ⚠️  Already exists or couldn't extract")
        
        # Strategy 3: Focused extraction prompts
        print("\n3️⃣ Focused extraction...")
        
        focused_prompts = []
        
        if "work" in text.lower():
            focused_prompts.append(f"Professional information from: {text}")
        
        if any(word in text.lower() for word in ["use", "using", "utilize"]):
            focused_prompts.append(f"Tools and technologies mentioned: {text}")
        
        if any(word in text.lower() for word in ["like", "love", "enjoy", "prefer"]):
            focused_prompts.append(f"Personal preferences from: {text}")
        
        if any(word in text.lower() for word in ["live", "from", "located", "based"]):
            focused_prompts.append(f"Location information: {text}")
        
        for prompt in focused_prompts:
            result = self.create_memory_with_context(prompt, user_id, app)
            if result:
                print(f"   ✅ Extracted: {result.get('content')}")
                memories_created.append(result)
                time.sleep(1)
        
        # Get final stats
        stats_after = requests.get(f"{self.stats_url}?user_id={user_id}").json()
        final_count = stats_after.get('total_memories', 0)
        
        print(f"\n📊 Summary:")
        print(f"   Initial memories: {initial_count}")
        print(f"   Final memories: {final_count}")
        print(f"   New memories created: {final_count - initial_count}")
        print(f"   Unique facts extracted: {len(set(m.get('content', '') for m in memories_created))}")
        
        return memories_created

def main():
    forcer = MultiMemoryForcer()
    
    # Test cases with multiple facts
    test_cases = [
        "I am Alex, I work at Publicis Groupe as a senior developer, I specialize in Python and data automation, and I live in Seattle",
        "I love hiking on weekends, my favorite mountain is Mount Rainier, I also enjoy photography, and I prefer using Canon cameras",
        "I use Python for backend development, JavaScript for frontend work, Docker for containerization, and VS Code as my IDE"
    ]
    
    for test in test_cases:
        memories = forcer.force_multi_memory_creation(test)
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()