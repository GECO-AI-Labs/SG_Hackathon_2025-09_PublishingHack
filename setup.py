#!/usr/bin/env python3
"""
World Scientific Publishing - One-Click Setup
Simple but AI-Enhanced deployment
"""

import os
import sys
import subprocess

def create_env_file():
    """Create .env configuration file"""
    env_content = """# World Scientific Publishing - AI Sales Assistant Configuration

# Database Settings (Update these with your MySQL details)
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=temp

# OpenAI API Settings (Update with your Bitdeer OpenAI key)
OPENAI_API_KEY=your-api-key-here

# Optional: Advanced Settings
OPENAI_MODEL=gpt-3.5-turbo
OPENAI_TEMPERATURE=0.3
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✅ Created .env file")
        return True
    else:
        print("ℹ️  .env file already exists")
        return True

def create_requirements():
    """Create requirements.txt"""
    requirements = """Flask==2.3.3
Flask-CORS==4.0.0
mysql-connector-python==8.1.0
openai==0.28.1
pandas==2.0.3
python-dotenv==1.0.0"""
    
    with open('requirements.txt', 'w') as f:
        f.write(requirements)
    print("✅ Created requirements.txt")

def create_readme():
    """Create README.md"""
    readme_content = """# World Scientific Publishing - AI Sales Assistant

🚀 **Simple but AI-Enhanced Sales Intelligence System**

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure:**
   - Edit `.env` file
   - Set `DB_PASSWORD` for your MySQL database
   - Set `OPENAI_API_KEY` with your Bitdeer OpenAI key

3. **Run:**
   ```bash
   python app.py
   ```

4. **Use:**
   - Open `dashboard.html` in your browser
   - Try: "Sales team visiting China - which universities to prioritize?"

## 🤖 AI Features

- **Smart Query Understanding** - Natural language processing
- **Automated Insights** - AI-generated business recommendations  
- **Pattern Matching** - Fast responses for common queries
- **University Prioritization** - Intelligent ranking system

## 📊 Sample Queries

- "Sales team visiting China - which universities to prioritize?"
- "Top 10 most productive authors in computer science"
- "Revenue analysis by country for 2024"
- "Which journals perform best in Singapore?"

## 🛠️ Files

- `app.py` - AI-enhanced backend server
- `dashboard.html` - Interactive frontend dashboard
- `.env` - Configuration (update this!)
- `requirements.txt` - Python dependencies

## 💡 Business Value

Transform your database into an intelligent assistant that:
- ✅ Prioritizes universities for sales visits
- ✅ Identifies top authors for partnerships
- ✅ Analyzes revenue trends across markets
- ✅ Provides actionable business insights

Perfect for World Scientific Publishing's sales and marketing teams!
"""
    
    with open('README.md', 'w') as f:
        f.write(readme_content)
    print("✅ Created README.md")

def install_dependencies():
    """Install Python dependencies"""
    try:
        print("📦 Installing dependencies...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Failed to install dependencies")
        print("💡 Run manually: pip install -r requirements.txt")
        return False

def main():
    """One-click setup process"""
    print("🚀 WORLD SCIENTIFIC PUBLISHING")
    print("   AI-Enhanced Sales Assistant Setup")
    print("=" * 50)
    
    # Create files
    steps = [
        ("Creating .env configuration", create_env_file),
        ("Creating requirements.txt", create_requirements), 
        ("Creating README.md", create_readme),
        ("Installing dependencies", install_dependencies)
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        try:
            success = step_func()
            if not success:
                print(f"⚠️  {step_name} completed with issues")
        except Exception as e:
            print(f"❌ {step_name} failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 SETUP COMPLETE!")
    print("=" * 50)
    print("\n📝 NEXT STEPS:")
    print("1. Edit .env file:")
    print("   - Set DB_PASSWORD for MySQL")
    print("   - Set OPENAI_API_KEY with your Bitdeer key")
    print("\n2. Start the system:")
    print("   python app.py")
    print("\n3. Open dashboard.html in your browser")
    print("\n4. Try sample query:")
    print("   'Sales team visiting China - which universities to prioritize?'")
    print("\n" + "=" * 50)
    print("💡 All files are ready in current directory")
    print("📁 Simple structure: app.py + dashboard.html + .env")
    print("🤖 AI-enhanced with smart insights and recommendations")

if __name__ == '__main__':
    main()