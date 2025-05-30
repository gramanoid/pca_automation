# LLM Memory System - Best Practices & Recommendations

## Overview

For the Media Plan to Raw Data project, I recommend a **hybrid approach** that combines:
1. **Persistent local memory** for learned patterns
2. **Dynamic context injection** for relevant information
3. **Static domain knowledge** for industry standards

## Architecture Comparison

### Option 1: Inject Full Context Every Time
```python
# Simple but expensive
prompt = f"""
You are an expert in media planning...
[500 lines of context]
[Previous mappings]
[Validation rules]
[Domain knowledge]

Now map these columns: {columns}
"""
```

**Pros:**
- Simple implementation
- No state management
- Always has full context

**Cons:**
- High token usage ($$$)
- Slower responses
- Redundant information
- Context window limits

### Option 2: Local Memory File (RECOMMENDED) ✅
```python
# Smart and efficient
memory = LLMMemoryManager()
context = memory.get_relevant_context(task_type='column_mapping')
prompt = f"""
{context}  # Only relevant memories

Map these columns: {columns}
"""
```

**Pros:**
- Efficient token usage
- Learns and improves
- Fast lookups
- Persistent knowledge

**Cons:**
- More complex setup
- Needs maintenance
- Storage requirements

## Recommended Implementation

### 1. **Three-Tier Memory System**

```
┌─────────────────────────────────────┐
│         Static Layer                │
│   (Domain Knowledge - Rarely Changes)│
├─────────────────────────────────────┤
│        Dynamic Layer                │
│   (Learned Patterns - Updates Daily) │
├─────────────────────────────────────┤
│        Session Layer                │
│   (Current Task Context - Temporary) │
└─────────────────────────────────────┘
```

### 2. **Memory Structure**

```
llm_memory/
├── domain_knowledge.md          # Static industry knowledge
├── llm_memory.db               # SQLite for structured queries
├── base_prompts.yaml           # Prompt templates
├── mappings.json               # Learned column mappings
├── validations.json            # Learned validation rules
└── cache/                      # Temporary session data
    └── responses_2025-05-28.pkl
```

### 3. **Smart Context Selection**

Instead of sending everything, select relevant context:

```python
def get_relevant_context(task_type, current_data):
    context = []
    
    # Always include core domain knowledge
    context.append(get_domain_essentials())  # ~200 tokens
    
    # Add task-specific memories
    if task_type == 'column_mapping':
        # Get top 10 most used mappings
        context.append(get_top_mappings(10))  # ~100 tokens
        
        # Get mappings similar to current columns
        similar = find_similar_columns(current_data.columns)
        context.append(similar)  # ~50 tokens
    
    # Total: ~350 tokens vs 2000+ for full context
    return '\n'.join(context)
```

## Best Practices

### 1. **Memory Lifecycle Management**

```python
# Good: Track success and update confidence
mapping = llm.map_column("SPEND_USD")
if user_confirms_mapping:
    memory.update_success_rate("SPEND_USD", success=True)
    memory.increment_confidence("SPEND_USD", 0.05)
else:
    memory.update_success_rate("SPEND_USD", success=False)
    memory.decrease_confidence("SPEND_USD", 0.1)
```

### 2. **Efficient Caching**

```python
# Cache expensive operations
@cache_with_ttl(hours=24)
def get_platform_validation_rules(platform):
    return llm.generate_validation_rules(platform)

# Use cache for repeated operations
rules = get_platform_validation_rules("DV360")  # First call: LLM
rules = get_platform_validation_rules("DV360")  # Second call: Cache
```

### 3. **Prompt Template Management**

```yaml
# base_prompts.yaml
column_mapping:
  system: "You are a media planning data expert."
  context_slots:
    - domain_knowledge
    - recent_mappings
    - similar_patterns
  user_template: |
    {context}
    
    Map these source columns to target columns:
    Source: {source_columns}
    Target: {target_columns}
    
    Return JSON with confidence scores.
```

### 4. **Fallback Strategies**

```python
def map_with_fallback(source_col, target_cols):
    # Try memory first (fast)
    memory_result = memory.recall('mappings', source_col)
    if memory_result and memory_result['confidence'] > 0.8:
        return memory_result
    
    # Try rule-based (medium)
    rule_result = apply_mapping_rules(source_col, target_cols)
    if rule_result:
        return rule_result
    
    # Use LLM (expensive but accurate)
    llm_result = llm.map_column(source_col, target_cols)
    memory.remember('mappings', source_col, llm_result)
    return llm_result
```

## Implementation Roadmap

### Phase 1: Basic Memory (1 day)
- Set up SQLite database
- Implement basic remember/recall
- Create domain knowledge file

### Phase 2: Smart Context (2 days)
- Implement relevance scoring
- Build prompt templates
- Add caching layer

### Phase 3: Learning System (2 days)
- Track success rates
- Implement confidence updates
- Add feedback loop

### Phase 4: Optimization (1 day)
- Compress old memories
- Implement memory pruning
- Add performance monitoring

## Cost Analysis

| Approach | Tokens/Request | Cost/1000 Requests | Speed |
|----------|---------------|-------------------|--------|
| Full Context | 2000-3000 | $60-90 | Slow |
| Smart Memory | 300-500 | $9-15 | Fast |
| Hybrid (Recommended) | 400-600 | $12-18 | Medium |

## Memory Maintenance

### Daily Tasks
```python
# Run daily maintenance
memory.prune_low_confidence_entries(threshold=0.3)
memory.archive_old_entries(days=30)
memory.optimize_database()
```

### Weekly Tasks
```python
# Analyze and improve
report = memory.generate_performance_report()
memory.retrain_low_performers(report.failing_mappings)
memory.export_backup("weekly_backup.json")
```

## Security Considerations

1. **No Sensitive Data in Memory**
   - Don't store actual campaign data
   - Only store patterns and mappings

2. **Access Control**
   ```python
   memory = LLMMemoryManager(
       memory_dir=Path("llm_memory"),
       encryption_key=os.getenv("MEMORY_ENCRYPTION_KEY")
   )
   ```

3. **Audit Trail**
   ```python
   memory.log_access(user_id, action, timestamp)
   ```

## Conclusion

**Recommendation**: Use the **Local Memory System** with smart context injection:

1. **Reduces costs** by 80% through efficient token usage
2. **Improves accuracy** through learning
3. **Speeds up responses** with caching
4. **Maintains consistency** across sessions

The initial setup investment (~1 week) pays off quickly through reduced API costs and improved accuracy.