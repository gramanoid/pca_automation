# Operational Runbook - Media Plan to Raw Data Automation

**Last Updated:** May 28, 2025  
**Version:** 1.0  
**Audience:** Operations Team

## 🚨 Emergency Contacts

- **Technical Lead:** [Contact Info]
- **Backup Support:** [Contact Info]
- **Escalation:** [Manager Contact]

## 📋 Table of Contents

1. [Daily Operations](#daily-operations)
2. [Standard Procedures](#standard-procedures)
3. [Troubleshooting Guide](#troubleshooting-guide)
4. [Error Recovery](#error-recovery)
5. [Escalation Procedures](#escalation-procedures)
6. [Maintenance Tasks](#maintenance-tasks)

## Daily Operations

### Pre-Processing Checklist

- [ ] Verify input files are in correct format
- [ ] Check file naming conventions
- [ ] Ensure output directory has sufficient space
- [ ] Verify API key is set (if using Claude)
- [ ] Check previous day's logs for issues

### Running the Automation

#### Standard Processing - Complete Workflow
```bash
# 1. Navigate to project directory
cd /path/to/media-plan-automation

# 2. Activate virtual environment
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# 3. Run complete workflow
python production_workflow/orchestration/run_complete_workflow.py
```

#### Manual Step-by-Step Processing
```bash
# 1. Run extraction
python production_workflow/01_data_extraction/extract_and_combine_data.py \
  --planned input/PLANNED_*.xlsx \
  --delivered input/DELIVERED_*.xlsx \
  --output output/ \
  --combine

# 2. Run mapping
python production_workflow/03_template_mapping/map_to_template.py \
  --input output/COMBINED_*.xlsx \
  --template input/OUTPUT_TEMPLATE_FILE_EMPTY_FILE.xlsx \
  --output output/final_mapped_$(date +%Y%m%d).xlsx
```

#### With Client-Specific Rules
```bash
export CLIENT_ID=sensodyne  # Set client
python production_workflow/03_template_mapping/map_to_template.py [same arguments as above]
```

### Post-Processing Verification

1. **Check Output Files**
   - Verify output file exists
   - Check file size is reasonable (>100KB)
   - Open file to verify data is present

2. **Review Reports**
   - Check `*_VALIDATION_REPORT.txt` for errors
   - Review `*_COMPREHENSIVE_REPORT.txt` for coverage
   - Check `*_PERFORMANCE_REPORT.txt` for timing

3. **Log Review**
   ```bash
   # Check for errors
   grep -i error logs/excel_processor.log
   grep -i error production_workflow/05_monitoring/logs/*.log
   
   # Check completion
   tail -n 50 logs/excel_processor.log
   ```

## Standard Procedures

### Adding New Client Rules

1. Edit `config/client_mapping_rules.json`
2. Add client section:
   ```json
   "new_client": {
     "column_mappings": {
       "SOURCE_COLUMN": "TARGET_COLUMN"
     },
     "value_transformations": {
       "COLUMN_NAME": {
         "old_value": "new_value"
       }
     }
   }
   ```
3. Test with sample data
4. Document changes in client folder

### Handling Large Files (>100MB)

1. **Split Processing**
   ```bash
   # Process platforms separately
   python production_workflow/01_data_extraction/extract_and_combine_data.py \
     --delivered input/DELIVERED_*.xlsx \
     --output output/ \
     --platform DV360
   ```

2. **Increase Memory**
   ```bash
   export PYTHON_MEMORY_LIMIT=4G
   ```

3. **Monitor Progress**
   - Watch progress bars
   - Check memory usage: `top` or Task Manager

### Monthly Maintenance

- [ ] Archive old output files (>30 days)
- [ ] Clean up log files (keep last 30 days)
- [ ] Update client mapping rules
- [ ] Review error patterns
- [ ] Update documentation

## Troubleshooting Guide

### Common Issues and Solutions

#### 1. "File not found" Error
**Symptom:** `FileNotFoundError: [Errno 2] No such file or directory`

**Solution:**
- Check file exists in input directory
- Verify file permissions
- Check file naming pattern matches

#### 2. "Memory Error"
**Symptom:** `MemoryError` or system becomes slow

**Solution:**
```bash
# Process in smaller chunks
python production_workflow/01_data_extraction/extract_and_combine_data.py \
  --delivered input/DELIVERED_*.xlsx \
  --output output/ \
  --chunk-size 1000
```

#### 3. "API Key Error"
**Symptom:** `No Anthropic API key found`

**Solution:**
```bash
# Set API key
export ANTHROPIC_API_KEY=sk-ant-api03-xxx
# Or add to .bashrc/.bash_profile
```

#### 4. "Mapping Coverage < 100%"
**Symptom:** Report shows coverage below 100%

**Check:**
1. Review unmapped columns in report
2. Check for new column names
3. Update mappings if needed
4. Re-run with updated config

#### 5. "R&F Data Missing"
**Symptom:** R&F metrics show 0 or missing

**Solution:**
1. Check Source_Sheet contains "_RF" suffix
2. Verify PLATFORM column has metric names
3. Check UNIQUES_REACH column has data
4. Review R&F validation report

### Debug Mode

Enable detailed logging:
```bash
export EXCEL_EXTRACTOR_LOG_LEVEL=DEBUG
export MAPPER_LOG_LEVEL=DEBUG
# Run commands as normal
```

## Error Recovery

### Partial Processing Failure

1. **Identify Last Successful Step**
   ```bash
   ls -la output/ | grep $(date +%Y%m%d)
   ```

2. **Resume from Checkpoint**
   - If extraction succeeded: Skip to mapping
   - If mapping failed: Re-run with existing COMBINED file

3. **Verify Data Integrity**
   ```bash
   python validate_deployment.py --check-data output/COMBINED_*.xlsx
   ```

### Complete Processing Failure

1. **Collect Diagnostic Info**
   ```bash
   # Create diagnostic package
   mkdir diagnostic_$(date +%Y%m%d_%H%M%S)
   cp main_scripts/logs/*.log diagnostic_*/
   cp output/*_REPORT.txt diagnostic_*/ 2>/dev/null
   tar -czf diagnostic_*.tar.gz diagnostic_*/
   ```

2. **Clear and Retry**
   ```bash
   # Clear output directory
   mkdir -p output/backup_$(date +%Y%m%d)
   mv output/*.xlsx output/backup_*/
   
   # Retry processing
   ```

3. **Escalate if Needed**
   - Send diagnostic package to technical team
   - Include error messages and steps taken

## Escalation Procedures

### Level 1: Operations Team (0-30 minutes)
- Check runbook troubleshooting guide
- Verify inputs and environment
- Attempt basic recovery steps
- Document issue in incident log

### Level 2: Technical Support (30-60 minutes)
- Review diagnostic logs
- Check for system issues
- Verify API connectivity
- Attempt advanced recovery

### Level 3: Development Team (60+ minutes)
- Code-level debugging required
- New error type encountered
- Data corruption suspected
- Performance degradation

### Incident Log Template
```
Date: [YYYY-MM-DD HH:MM]
Operator: [Name]
Issue: [Brief description]
Impact: [Files affected, users impacted]
Steps Taken: 
1. [Action 1]
2. [Action 2]
Resolution: [How resolved or escalated]
Follow-up: [Any required actions]
```

## Maintenance Tasks

### Daily
- [ ] Check processing completion
- [ ] Review error logs
- [ ] Verify output quality
- [ ] Update processing metrics

### Weekly
- [ ] Archive processed files
- [ ] Clean temporary files
- [ ] Review performance trends
- [ ] Update client configurations

### Monthly
- [ ] Full system backup
- [ ] Performance analysis
- [ ] Update documentation
- [ ] Review and optimize rules

### Quarterly
- [ ] Accuracy audit
- [ ] System performance review
- [ ] Training update
- [ ] Process improvement review

## Quick Reference Commands

```bash
# Check system status
python validate_deployment.py

# View recent errors
grep -i error main_scripts/logs/*.log | tail -20

# Check processing history
ls -la output/ | grep xlsx | tail -10

# Monitor real-time processing
tail -f main_scripts/logs/simple_llm_mapper.log

# Emergency stop
Ctrl+C (then cleanup partial files)

# Validate output file
python -c "import pandas as pd; df=pd.read_excel('output/final_mapped.xlsx'); print(f'Rows: {len(df)}, Columns: {len(df.columns)}')"
```

## Performance Benchmarks

Expected processing times:
- Small files (<10MB): 1-2 minutes
- Medium files (10-50MB): 3-5 minutes
- Large files (50-100MB): 5-10 minutes
- Very large files (>100MB): 10-20 minutes

If processing exceeds 2x expected time, investigate.

---

**Remember:** When in doubt, document the issue and escalate. Better to ask for help than risk data quality issues.