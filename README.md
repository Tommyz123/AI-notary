# Notary Training System

A professional notary training platform with AI-powered explanations, dynamic quizzes, and comprehensive progress tracking.

## 🚀 Quick Start

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Environment Setup
1. Copy the `.env` file and configure your API key:
```bash
cp .env .env.local
```

2. Edit `.env.local` file and set your DeepSeek API key:
```
DEEPSEEK_API_KEY=your_api_key_here
```

### Database Setup
Run the migration script to set up the database:
```bash
python migrate_data.py
```

### Run Application
```bash
streamlit run app.py
```

### Default Login
- Username: `admin`
- Password: `admin123`

**⚠️ Important: Change the admin password after first login!**

### Speed Optimization (Recommended)
For faster AI responses, configure OpenAI API:
```bash
python3 setup_openai.py
```
This will:
- Switch to OpenAI's faster API
- Enable intelligent caching
- Optimize parameters for speed
- Provide 2-5x faster responses

## 🔧 Configuration

### Environment Variables

#### API Configuration
- `API_PROVIDER`: Set to "openai" or "deepseek" 
- `OPENAI_API_KEY`: OpenAI API key (for faster responses)
- `OPENAI_MODEL`: OpenAI model (gpt-3.5-turbo, gpt-4, etc.)
- `DEEPSEEK_API_KEY`: DeepSeek API key (alternative)
- `DEEPSEEK_MODEL`: DeepSeek model name

#### Performance Settings
- `ENABLE_RESPONSE_CACHING`: Enable intelligent caching (true/false)
- `CACHE_DURATION_MINUTES`: Cache retention time (default: 60)
- `MAX_CONTENT_LENGTH`: Maximum content length limit
- `RATE_LIMIT_PER_MINUTE`: API call rate limiting

## 🔒 Security Features

- ✅ Environment variable configuration management
- ✅ User input validation and sanitization
- ✅ XSS protection
- ✅ Content length restrictions
- ✅ API rate limiting
- ✅ User authentication system
- ✅ Session management
- ✅ Role-based access control

## 📁 Project Structure

```
notary6/
├── app.py                     # Main application entry
├── config.py                  # Configuration management
├── database.py                # SQLite database operations
├── auth.py                    # Authentication system
├── analytics.py               # User analytics and visualization
├── admin_panel.py             # Admin management interface
├── deepseek_api.py            # API calling wrapper
├── dynamic_quiz_generator.py  # Dynamic quiz generation
├── migrate_data.py            # Database migration script
├── progress.py                # Legacy progress management
├── completed_tracker.py       # Legacy completion tracking
├── teaching_controller.py     # Teaching controller
├── lessons.csv                # Course content data
├── prompt_template.txt        # AI prompt template
├── requirements.txt           # Dependencies list
├── .env                       # Environment variables template
├── .gitignore                 # Git ignore file
└── README.md                  # This file
```

## ✨ Latest Improvements

### Phase 1: Security & Configuration Management ✅
- [x] Environment variable configuration
- [x] Remove hardcoded API keys
- [x] Input validation and XSS protection
- [x] Content length restrictions
- [x] .gitignore for sensitive information

### Phase 2: Database & Multi-user Support ✅
- [x] SQLite database integration
- [x] User authentication system
- [x] Multi-user progress tracking
- [x] Session management
- [x] Data migration from JSON/CSV

### Phase 3: Analytics & Admin Features ✅
- [x] User analytics dashboard
- [x] Progress visualization
- [x] Quiz performance tracking
- [x] Admin panel for user management
- [x] System administration tools

### Next Phase (In Progress)
- [ ] Enhanced caching with database
- [ ] Performance optimizations
- [ ] Responsive UI design
- [ ] Offline mode support
- [ ] Advanced learning analytics

## 🎯 User Guide

### For Students:
1. **Course Learning**: Browse sidebar to select lessons, choose from three explanation depths
2. **Dynamic Quizzes**: Auto-generated relevant test questions for each lesson
3. **Progress Tracking**: Mark completion status, automatic progress saving
4. **Smart Q&A**: Ask questions about lesson content, get AI responses
5. **Final Assessment**: Comprehensive 50-question evaluation
6. **Analytics**: View your learning progress and performance metrics

### For Administrators:
1. **User Management**: Create, modify, and manage user accounts
2. **Content Management**: Add, edit, and organize lesson content
3. **System Analytics**: Monitor platform usage and performance
4. **Database Management**: Backup, maintenance, and configuration

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Backend**: Python 3.8+
- **Database**: SQLite
- **AI Service**: DeepSeek API
- **Analytics**: Plotly
- **Authentication**: Custom session-based system
- **Data Storage**: Database-driven with CSV fallback