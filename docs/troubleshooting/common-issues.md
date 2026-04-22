### common issues

1. **ollama connection error**:
   ```bash
   # check if ollama is running
   curl http://localhost:11434/api/tags
   
   # start ollama if needed
   ollama serve
   ```

2. **model loading issues**:
   ```bash
   # clear model cache
   rm -rf ./model_cache
   
   # reinstall sentence-transformers
   pip uninstall sentence-transformers
   pip install sentence-transformers
   ```

3. **excel reading errors**:
   - ensure excel file has correct column names
   - check file format (xlsx/xls)
   - verify file isn't corrupted

4. **memory issues**:
   - reduce `MAX_NEWS_DOCUMENTS` in config
   - use smaller language models
   - increase system ram or use cloud deployment
