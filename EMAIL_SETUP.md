# 📧 Forgot Password & Email OTP Setup Guide

## 🚀 Quick Start (Development Mode)

Your forgot password system is now ready to use with **Console Email Mode** enabled!

### What this means:
- OTPs and password reset emails are **printed to the console** instead of being sent
- Perfect for **testing and development**
- No real email credentials needed
- No email server required

### Test it now:
1. Go to Student Login: `http://127.0.0.1:8000/login/`
2. Click "Forgot Password?"
3. Enter a registered email (e.g., your test student account's email)
4. Click "Send OTP"
5. Check your **Django development server console/terminal** - you'll see the OTP printed there!
6. Copy the OTP and continue with password reset

---

## 📋 Requirements

✓ `python-dotenv` - already installed
✓ `.env` file - already created in project root
✓ Console Email Backend - already configured

---

## 🔧 Production Setup (Real Email)

When you're ready to send real emails, follow these steps:

### Step 1: Using Gmail (Recommended for small projects)

1. **Enable 2-Step Verification** in your Google Account:
   - Go to https://myaccount.google.com/security
   - Enable 2-Step Verification

2. **Create an App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Select: Mail → Windows Computer
   - Copy the 16-character password (with spaces)

3. **Edit `.env` file**:
   ```
   USE_CONSOLE_EMAIL=False
   EMAIL_HOST=smtp.gmail.com
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
   ```

4. **Restart Django**:
   ```bash
   python manage.py runserver
   ```

### Step 2: Using Other Email Providers

**Office365:**
```
USE_CONSOLE_EMAIL=False
EMAIL_HOST=smtp.office365.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@outlook.com
EMAIL_HOST_PASSWORD=your-password
```

**SendGrid:**
```
USE_CONSOLE_EMAIL=False
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.xxxxxxxxxxxxxxxx
```

**AWS SES:**
```
USE_CONSOLE_EMAIL=False
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-ses-username
EMAIL_HOST_PASSWORD=your-ses-password
```

---

## 🔒 Security Notes

⚠️ **IMPORTANT:** Never commit `.env` file to version control!

Your `.gitignore` should include:
```
.env
*.pyc
__pycache__/
db.sqlite3
media/
```

---

## 🧪 Testing Email (Development)

The system will print emails to your Django console like this:

```
Subject: Password Reset OTP
From: your-email@gmail.com
To: student@example.com
Body:
Hello Student,
Your OTP for password reset is: 123456
...
```

Just copy the OTP and paste it in the verify page!

---

## 📞 Email Flow Summary

1. **Student clicks "Forgot Password?"**
   - Redirects to `/forgot-password/`

2. **Student enters email**
   - System generates 6-digit OTP
   - OTP printed to console (dev) OR sent via email (prod)
   - OTP stored in session (10 min expiry)
   - Redirects to `/verify-otp/`

3. **Student enters OTP + new password**
   - OTP validated
   - Password updated in database
   - Session cleared
   - Success message shown
   - Link to login provided

4. **Student logs in with new password**
   - Uses enrollment number + new password
   - Login successful!

---

## ✅ Troubleshooting

### Issue: "Failed to send email" error

**Solution 1: Check .env file**
```powershell
# Windows PowerShell
Get-Content .env
```

Should show:
```
USE_CONSOLE_EMAIL=True
```

**Solution 2: Restart Django**
```bash
python manage.py runserver
```

**Solution 3: For Gmail - Check App Password**
- Ensure you created 16-character **App Password** (not regular password)
- Must enable 2-Step Verification first
- Password should have spaces like: `xxxx xxxx xxxx xxxx`

### Issue: OTP not appearing in console

- Make sure you're looking at the Django development server terminal
- It should appear as "Subject: Password Reset OTP"
- Scroll up in your terminal if needed

### Issue: "Session expired" after sending OTP

- OTP is valid for 10 minutes
- If more time passed, request a new OTP
- Session data is stored locally in Django

---

## 📊 File Structure

```
QuizWithAdmin-master/
├── .env                          # Environment variables (dev config)
├── .env.example                  # Template for .env setup
├── test_email_config.py          # Email configuration test
├── requirements.txt              # Updated with python-dotenv
├── stu_test/
│   └── settings.py              # Updated email config
├── quiz/
│   ├── views.py                 # Added forgot_password_view, verify_otp_view
│   ├── forms.py                 # Added ForgotPasswordForm, OTPVerificationForm
│   ├── urls.py                  # Added /forgot-password/ and /verify-otp/ routes
│   └── templates/
│       ├── stu_login.html       # Updated with "Forgot Password?" link
│       ├── forgot_password.html  # Request email page
│       └── verify_otp.html      # OTP verification & password reset page
```

---

## 🎯 Quick Reference

| Feature | Development | Production |
|---------|-------------|-----------|
| Email Delivery | Console output | Real SMTP |
| Configuration | .env file | .env + credentials |
| OTP Handling | Print to terminal | Send to inbox |
| Session Expiry | 10 minutes | 10 minutes |
| Password Security | Django hashed | Django hashed |

---

## 💡 Tips

- **For rapid testing:** Stay in console mode, copy OTP from terminal
- **For realistic testing:** Set up Gmail App Password and test real email flow
- **For production:** Use environment variables, never hardcode credentials
- **For security:** Always use email with 2FA enabled (like Gmail with App Passwords)

---

## ✨ What's Included

✅ Forgot Password page (/forgot-password/)  
✅ OTP Verification page (/verify-otp/)  
✅ 6-digit OTP generation  
✅ 10-minute session expiry  
✅ Email sending (console or SMTP)  
✅ Password update with hashing  
✅ Error handling and validation  
✅ Responsive UI matching your design  
✅ Environment variable support  
✅ Ready for production  

Happy testing! 🎉
