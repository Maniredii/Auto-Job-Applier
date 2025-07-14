# API Setup Guide for LinkedIn AI Auto Job Applier

## 🔑 **Required API Keys**

### **1. OpenAI API Key (Primary - RECOMMENDED)**
- **Status**: ✅ **CONFIGURED** (Your key is already set)
- **Purpose**: 
  - Generate customized resumes for each job
  - Create personalized cover letters
  - Answer application questions intelligently
  - Extract skills from job descriptions
- **Cost**: ~$0.01-0.05 per job application
- **Setup**: Already configured in `config/secrets.py`

### **2. DeepSeek API Key (Alternative)**
- **Status**: ⚠️ **OPTIONAL** (Alternative to OpenAI)
- **Purpose**: Same as OpenAI but using DeepSeek models
- **Cost**: Generally cheaper than OpenAI
- **Setup**: Add your DeepSeek API key in `config/secrets.py`

---

## 🚀 **How to Get API Keys**

### **OpenAI API Key (Already Configured)**
1. **Visit**: https://platform.openai.com/api-keys
2. **Sign up/Login** to OpenAI account
3. **Click** "Create new secret key"
4. **Copy** the key (starts with `sk-`)
5. **Add** to `config/secrets.py` (Already done!)

### **DeepSeek API Key (Optional)**
1. **Visit**: https://platform.deepseek.com/
2. **Sign up/Login** to DeepSeek account
3. **Navigate** to API section
4. **Create** new API key
5. **Add** to `config/secrets.py`:
   ```python
   deepseek_api_key = "your_deepseek_key_here"
   ai_provider = "deepseek"
   ```

---

## ⚙️ **Configuration Settings**

### **Current Configuration** (`config/secrets.py`):
```python
# AI Settings
use_AI = True                    # ✅ AI features enabled
ai_provider = "openai"           # ✅ Using OpenAI
openai_api_key = "sk-proj-..."   # ✅ Your key configured
deepseek_api_key = ""            # ⚠️ Empty (not needed)
```

### **To Switch to DeepSeek**:
```python
ai_provider = "deepseek"
deepseek_api_key = "your_deepseek_key"
```

---

## 💰 **Cost Estimation**

### **OpenAI (GPT-3.5-turbo)**
- **Resume Generation**: ~$0.02 per job
- **Cover Letter**: ~$0.01 per job
- **Question Answering**: ~$0.005 per job
- **Total per application**: ~$0.035
- **100 applications**: ~$3.50

### **DeepSeek (Generally Cheaper)**
- **Total per application**: ~$0.02
- **100 applications**: ~$2.00

---

## 🧪 **Testing Your Setup**

Run the test script to verify your API configuration:

```bash
python test_enhanced_bot.py
```

This will test:
- ✅ OpenAI API connection
- ✅ Resume generation
- ✅ Cover letter generation
- ✅ Configuration validation

---

## 🔧 **Troubleshooting**

### **Common Issues:**

1. **"API key not found"**
   - Check if the key is correctly copied
   - Ensure no extra spaces

2. **"Rate limit exceeded"**
   - Wait a few minutes
   - Check your OpenAI account usage

3. **"Invalid API key"**
   - Verify the key format (starts with `sk-`)
   - Check if the key is active in your OpenAI account

4. **"Connection error"**
   - Check your internet connection
   - Try again in a few minutes

---

## 📊 **Usage Monitoring**

### **Monitor Your Usage:**
- **OpenAI**: https://platform.openai.com/usage
- **DeepSeek**: https://platform.deepseek.com/usage

### **Set Usage Limits:**
- **OpenAI**: Set spending limits in account settings
- **DeepSeek**: Configure usage limits in dashboard

---

## 🎯 **Recommended Settings**

### **For Best Results:**
```python
use_AI = True
ai_provider = "openai"  # More reliable and feature-rich
```

### **For Cost Optimization:**
```python
use_AI = True
ai_provider = "deepseek"  # Generally cheaper
```

---

## ✅ **Your Current Setup Status**

- ✅ **OpenAI API Key**: Configured
- ✅ **AI Features**: Enabled
- ✅ **Resume Customization**: Ready
- ✅ **Cover Letter Generation**: Ready
- ✅ **Smart Question Answering**: Ready

**You're all set to run the enhanced bot!** 🚀

---

## 🚀 **Next Steps**

1. **Test the setup**:
   ```bash
   python test_enhanced_bot.py
   ```

2. **Run the enhanced bot**:
   ```bash
   python runAiBot.py
   ```

3. **Monitor the results**:
   - Check `generated_resumes/` folder
   - Check `generated_cover_letters/` folder
   - View application history in `all excels/`

---

**Need Help?** Check the logs in the `logs/` folder for detailed error messages. 