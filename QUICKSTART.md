# البدء السريع / Quick Start

دليل سريع للبدء في استخدام Media Reels Generator.

Quick guide to get started with Media Reels Generator.

## التثبيت السريع / Quick Installation

### 1. تثبيت FFmpeg

**Windows:**
```powershell
winget install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### 2. تثبيت Python Packages

```bash
pip install -r requirements.txt
```

### 3. إعداد API Key

أنشئ ملف `.env`:
```env
OPENAI_API_KEY=your_key_here
```

## الاستخدام السريع / Quick Usage

### مثال 1: معالجة ملف فيديو

```bash
python run.py --input video.mp4 --n-highlights 5
```

### مثال 2: معالجة ملف صوتي

```bash
python run.py --input podcast.mp3 --n-highlights 3
```

### مثال 3: معالجة مجلد كامل

```bash
python run.py --input ./media_folder --out ./outputs --n-highlights 5
```

## النتيجة / Result

ستجد النتائج في:
```
outputs/
└── [filename]/
    ├── highlights.json
    ├── highlight_01/
    │   ├── clip.mp4
    │   ├── clip_1x1.mp4
    │   ├── clip_9x16.mp4
    │   ├── clip.srt
    │   └── caption.txt
    └── ...
```

## الخطوات التالية / Next Steps

1. راجع `README.md` للتفاصيل الكاملة
2. عدّل `config.yaml` حسب احتياجاتك
3. جرب خيارات مختلفة (اللغة، عدد النقاط المهمة، إلخ)

## مساعدة / Help

```bash
python run.py --help
```

---

**ملاحظة:** تأكد من وجود مفتاح OpenAI API صالح قبل البدء.

**Note:** Make sure you have a valid OpenAI API key before starting.

