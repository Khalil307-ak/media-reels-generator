# Media Reels Generator 🎬

مولد تلقائي لمقاطع الفيديو القصيرة (Reels) من ملفات الوسائط - أداة Python كاملة لإنشاء مقاطع فيديو قصيرة ملخصة من ملفات صوتية أو فيديو.

A complete Python tool to automatically generate short social media reels (highlights) from audio/video files with transcription, key point extraction, and multi-format output.

## المميزات / Features

- ✅ **نسخ تلقائي** - دعم OpenAI Whisper API أو Whisper المحلي
- ✅ **استخراج النقاط المهمة** - استخدام LLM (GPT) لتحديد أهم اللحظات
- ✅ **تنسيقات متعددة** - إنتاج مقاطع 1:1 (مربع) و 9:16 (عمودي) للتطبيقات الاجتماعية
- ✅ **ترجمات تلقائية** - إنشاء ملفات SRT وحرق الترجمات في الفيديو
- ✅ **دعم صيغ متعددة** - MP3, WAV, MP4, MKV, MOV وغيرها
- ✅ **معالجة متوازية** - معالجة عدة ملفات في نفس الوقت

## المتطلبات / Requirements

- Python 3.10 أو أحدث
- FFmpeg (يجب تثبيته في النظام)
- OpenAI API Key (للنسخ واستخراج النقاط المهمة) أو Whisper محلي

## التثبيت / Installation

### 1. تثبيت FFmpeg

**Windows:**
- تحميل من [ffmpeg.org](https://ffmpeg.org/download.html)
- أو استخدام: `winget install ffmpeg`

**Linux:**
```bash
sudo apt-get update
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

### 3. إعداد المفاتيح / Setup API Keys

#### الطريقة 1: ملف .env (موصى به)

أنشئ ملف `.env` في المجلد الرئيسي:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

#### الطريقة 2: config.yaml

عدّل ملف `config.yaml` وأضف مفتاح API:

```yaml
api:
  openai_api_key: "your_openai_api_key_here"
```

## الاستخدام / Usage

### مثال أساسي / Basic Example

```bash
# معالجة ملف واحد
python run.py --input video.mp4 --n-highlights 5

# معالجة مجلد كامل
python run.py --input ./media_folder --out ./outputs --n-highlights 3

# تحديد اللغة
python run.py --input audio.mp3 --lang ar --n-highlights 5

# معالجة متوازية لعدة ملفات
python run.py --input ./videos --parallel --n-highlights 5
```

### معاملات سطر الأوامر / CLI Arguments

```
--input, -i          ملف أو مجلد المدخلات (مطلوب)
--out, -o            مجلد الإخراج (افتراضي: outputs)
--n-highlights, -n   عدد النقاط المهمة لكل ملف
--lang, -l           كود اللغة (ar, en, fr, etc.) - تلقائي إذا لم يُحدد
--translate-to       كود اللغة للترجمة (اختياري)
--config             مسار ملف التكوين (افتراضي: config.yaml)
--confirm-copyright  تأكيد حقوق النشر
--parallel           معالجة متوازية لعدة ملفات
```

## هيكل الإخراج / Output Structure

```
outputs/
└── video_name/
    ├── highlights.json          # معلومات جميع النقاط المهمة
    ├── highlight_01/
    │   ├── clip.mp4             # المقطع الأساسي
    │   ├── clip_1x1.mp4         # نسخة مربعة (1080x1080)
    │   ├── clip_9x16.mp4        # نسخة عمودية (1080x1920)
    │   ├── clip.srt             # ملف الترجمات
    │   └── caption.txt          # العنوان والملخص
    ├── highlight_02/
    │   └── ...
    └── ...
```

## التكوين / Configuration

### استخدام Whisper المحلي / Using Local Whisper

في `config.yaml`:

```yaml
transcription:
  provider: "local_whisper"  # بدلاً من "openai"
  local_model: "base"         # tiny, base, small, medium, large
```

**ملاحظة:** النماذج الأكبر (medium, large) أكثر دقة لكنها أبطأ وتستهلك ذاكرة أكثر.

### تغيير عدد النقاط المهمة / Changing Highlight Count

```yaml
highlights:
  default_count: 5  # عدد النقاط المهمة الافتراضي
  min_duration: 6   # الحد الأدنى لمدة المقطع (ثواني)
  max_duration: 60  # الحد الأقصى لمدة المقطع (ثواني)
```

### جودة الفيديو / Video Quality

```yaml
video:
  crf: 23        # 18-28 (أقل = جودة أفضل، ملف أكبر)
  preset: "medium"  # ultrafast, fast, medium, slow
  burn_subtitles: true  # حرق الترجمات في الفيديو
```

## استخدام Replit / Using on Replit

### 1. رفع الملفات / Upload Files

- ارفع ملفات الوسائط إلى مجلد `media/` في Replit
- أو استخدم Secrets لإضافة API keys

### 2. إعداد Environment Variables

في Replit Secrets:
- `OPENAI_API_KEY` = your_api_key

### 3. تثبيت FFmpeg

في Replit Shell:
```bash
# Replit عادة يحتوي على ffmpeg، لكن إذا لم يكن موجوداً:
# استخدم Nix package manager أو ارفع نسخة محمولة
```

### 4. تشغيل / Run

```bash
python run.py --input ./media/video.mp4 --n-highlights 5
```

## استبدال مقدمي الخدمة / Switching Providers

### استبدال مقدم النسخ / Transcription Provider

**OpenAI Whisper API (افتراضي):**
```yaml
transcription:
  provider: "openai"
  model: "whisper-1"
```

**Whisper المحلي:**
```yaml
transcription:
  provider: "local_whisper"
  local_model: "base"
```

**Hugging Face:**
```yaml
transcription:
  provider: "huggingface"
  model_id: "openai/whisper-base"
```

### استبدال LLM لاستخراج النقاط المهمة

**OpenAI GPT (افتراضي):**
```yaml
highlights:
  llm_provider: "openai"
  llm_model: "gpt-4o-mini"  # أو "gpt-4", "gpt-3.5-turbo"
```

**Anthropic Claude:**
```yaml
highlights:
  llm_provider: "anthropic"
  llm_model: "claude-3-sonnet-20240229"
```

## أمثلة متقدمة / Advanced Examples

### معالجة ملف صوتي مع ترجمة

```bash
python run.py \
  --input podcast.mp3 \
  --lang ar \
  --translate-to en \
  --n-highlights 3
```

### إنتاج مقاطع قصيرة جداً

عدّل `config.yaml`:
```yaml
highlights:
  min_duration: 6
  max_duration: 15  # مقاطع قصيرة جداً
```

### معالجة مجلد كامل مع معالجة متوازية

```bash
python run.py \
  --input ./videos \
  --out ./reels_output \
  --n-highlights 5 \
  --parallel
```

## استكشاف الأخطاء / Troubleshooting

### خطأ: FFmpeg not found

**الحل:**
- تأكد من تثبيت FFmpeg
- أضف FFmpeg إلى PATH
- في Windows: أضف `C:\ffmpeg\bin` إلى PATH

### خطأ: OpenAI API key not found

**الحل:**
- تأكد من وجود `.env` مع `OPENAI_API_KEY`
- أو أضف المفتاح في `config.yaml`
- تحقق من أن المفتاح صحيح

### خطأ: Out of memory

**الحل:**
- استخدم نموذج Whisper أصغر (`tiny` أو `base`)
- قلل `crf` في إعدادات الفيديو
- عطّل المعالجة المتوازية

### الملفات الصوتية لا تُعالج

**الحل:**
- تأكد من أن FFmpeg يدعم الصيغة
- تحقق من أن الملف غير تالف
- جرب تحويل الملف إلى MP3 أولاً

### النقاط المهمة غير دقيقة

**الحل:**
- استخدم نموذج GPT أقوى (`gpt-4` بدلاً من `gpt-4o-mini`)
- زد `num_highlights` للحصول على خيارات أكثر
- راجع `temperature` في التكوين

### الملفات كبيرة جداً

**الحل:**
- زد `crf` (مثلاً 26-28) لتقليل حجم الملف
- استخدم `preset: "fast"` أو `"veryfast"`
- قلل دقة الإخراج في `formats`

## هيكل المشروع / Project Structure

```
media-reels-generator/
├── run.py              # نقطة الدخول الرئيسية
├── utils.py            # أدوات مساعدة
├── transcribe.py       # نسخ الصوت
├── highlight.py        # استخراج النقاط المهمة
├── editor.py           # تحرير الفيديو
├── config.yaml         # التكوين
├── requirements.txt    # المتطلبات
├── README.md           # هذا الملف
└── outputs/            # مجلد الإخراج (يُنشأ تلقائياً)
```

## الأداء / Performance Tips

1. **للحصول على سرعة أكبر:**
   - استخدم `local_model: "tiny"` أو `"base"`
   - استخدم `preset: "veryfast"` للفيديو
   - عطّل `burn_subtitles` إذا لم تكن ضرورية

2. **للحصول على جودة أفضل:**
   - استخدم `local_model: "medium"` أو `"large"`
   - استخدم `crf: 18-20`
   - استخدم `preset: "slow"`

3. **لتقليل استهلاك الذاكرة:**
   - عطّل المعالجة المتوازية
   - استخدم نماذج أصغر
   - معالجة ملف واحد في كل مرة

## الأمان وحقوق النشر / Security & Copyright

- الأداة تطبع تحذيراً عند معالجة محتوى من طرف ثالث
- استخدم `--confirm-copyright` لتأكيد أن لديك الحقوق
- لا تشارك ملفات `.env` أو `config.yaml` التي تحتوي على مفاتيح API

## الترخيص / License

هذا المشروع مفتوح المصدر. استخدمه بحرية ولكن تأكد من احترام حقوق النشر للمحتوى الذي تعالجه.

## المساهمة / Contributing

نرحب بالمساهمات! يرجى فتح Issue أو Pull Request.

## الدعم / Support

للأسئلة والمشاكل:
1. راجع قسم استكشاف الأخطاء أعلاه
2. افتح Issue على GitHub
3. راجع السجلات في `processing.log`

---

**ملاحظة:** هذا المشروع يستخدم OpenAI API و FFmpeg. تأكد من فهم تكاليف API قبل المعالجة الكبيرة.

**Note:** This project uses OpenAI API and FFmpeg. Make sure to understand API costs before large-scale processing.

