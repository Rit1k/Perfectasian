# Perfect Asian Interiors Backend

## Setup Instructions

1. **Install dependencies**

```
pip install -r requirements.txt
```

2. **Set up environment variables**

Create a `.env` file in the `backend/` directory with the following content:

```
SENDGRID_API_KEY=your_sendgrid_api_key_here
```

3. **Run the Flask app**

```
python app.py
```

The backend will be available at `http://localhost:5000` by default.

---

### Notes
- The contact form uses SendGrid to send emails. You must provide a valid SendGrid API key in the `.env` file.
- For local frontend-backend development, CORS is enabled.
- If you want to enable reCAPTCHA, you can add the widget to the form and verify the token in the `/contact` route. 