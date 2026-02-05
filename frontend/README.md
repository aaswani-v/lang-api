# वाणीCheck - Deepfake Audio Detection Frontend

A clean, modern web interface for detecting deepfake audio using AI.

## 📸 Features

- **Upload Audio Files** - Drag & drop or click to upload
- **Multi-Language Support** - English, Hindi, Tamil, Telugu, Malayalam
- **Real-time Detection** - Instant deepfake analysis
- **Confidence Scores** - Visual representation of detection confidence
- **Detailed Results** - Processing time, language, duration
- **Mobile Responsive** - Works on all devices
- **Live Backend Integration** - Connected to Railway-deployed API

## 📂 Files

```
frontend/
├── index.html              # Main page structure
├── style.css              # Professional styling
├── script.js              # API integration logic
├── DEPLOYMENT_GUIDE.md    # Complete deployment instructions
└── README.md              # This file
```

## 🚀 Quick Start

### Local Testing
```bash
# Python 3
python -m http.server 8000

# Then open: http://localhost:8000
```

### Deploy to Netlify (1 click!)
1. Go to https://app.netlify.com
2. Drag and drop this folder
3. Done! Your site is live

### Deploy to Vercel
1. Go to https://vercel.com
2. Click "Add new project"
3. Upload folder
4. Done!

### Deploy to GitHub Pages
1. Create GitHub repo
2. Push files
3. Enable Pages in settings
4. Done!

See `DEPLOYMENT_GUIDE.md` for detailed instructions.

## 🎨 UI Features

- **Gradient Background** - Modern visual design
- **Smooth Animations** - Polished interactions
- **Color-coded Results** - Red (deepfake), Yellow (uncertain), Green (genuine)
- **Loading State** - Shows progress while analyzing
- **Error Notifications** - User-friendly error messages
- **Responsive Grid** - Adapts to all screen sizes

## 🔌 API Integration

- **Endpoint**: `https://lang-api-production.up.railway.app/v1/detect`
- **Method**: POST
- **Auth**: Bearer token included
- **Payload**: Base64 audio + language + format
- **Response**: Deepfake score, confidence, language detection

## 📝 Supported Formats

- WAV
- MP3
- OGG
- WebM
- FLAC
- Max size: 30MB

## 🎯 Use Cases

- Verify voice authenticity
- Detect AI-generated speech
- Identify voice cloning attempts
- Media verification
- Content authenticity checking

## 🏆 Hackathon Ready

- Clean, professional design
- Live API integration
- Production-ready code
- Complete documentation
- Easy deployment

## 🔒 Security

- API key stored in frontend (demo key visible)
- CORS-enabled for cross-origin requests
- HTTPS connection enforced
- File validation on both client and server

## 📱 Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+
- Mobile browsers (iOS Safari, Chrome Mobile)

## 🎓 Learning Resources

- Modern HTML5 standards
- CSS3 animations and gradients
- Fetch API for HTTP requests
- File handling with FileReader
- Form validation

## 💻 Customization

### Change Colors
Edit `:root` variables in `style.css`
```css
--primary: #1e40af;
--success: #10b981;
--danger: #ef4444;
```

### Change API Endpoint
Edit `script.js` line 3:
```javascript
const API_ENDPOINT = 'your-api-url';
```

### Add New Languages
Edit `script.js` select options in `index.html`:
```html
<option value="language_code">Language Name</option>
```

## 📄 License

Open source - free to use, modify, and deploy

## 🤝 Contributing

Suggestions welcome! Feel free to fork and improve.

## 📞 Support

Check `DEPLOYMENT_GUIDE.md` for troubleshooting and FAQ.

---

**Ready to deploy? Follow the `DEPLOYMENT_GUIDE.md` and you'll be live in 1 minute!** 🚀
