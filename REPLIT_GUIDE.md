# دليل الاستخدام على Replit / Replit Usage Guide

دليل خطوة بخطوة لاستخدام Media Reels Generator على Replit.

Step-by-step guide for using Media Reels Generator on Replit.

## الخطوة 1: إنشاء Repl جديد / Step 1: Create New Repl

1. اذهب إلى [Replit](https://replit.com)
2. انقر على "Create Repl"
3. اختر "Python" كـ Template
4. اسم المشروع: `media-reels-generator`

## الخطوة 2: رفع الملفات / Step 2: Upload Files

### رفع ملفات الكود

انسخ جميع ملفات المشروع إلى Repl:
- `run.py`
- `utils.py`
- `transcribe.py`
- `highlight.py`
- `editor.py`
- `config.yaml`
- `requirements.txt`
- `README.md`

### رفع ملفات الوسائط

1. أنشئ مجلد `media/` في Repl
2. ارفع ملفاتك الصوتية/الفيديو إلى `media/`
3. الصيغ المدعومة: MP3, WAV, MP4, MKV, MOV

**ملاحظة:** Replit له حد حجم للملفات. للملفات الكبيرة، استخدم:
- رفع إلى Google Drive/Dropbox وربطها
- أو استخدم Replit Database

## الخطوة 3: تثبيت المتطلبات / Step 3: Install Requirements

في Replit Shell:

```bash
pip install -r requirements.txt
```

**ملاحظة:** قد يستغرق التثبيت بضع دقائق.

## الخطوة 4: إعداد FFmpeg / Step 4: Setup FFmpeg

Replit عادة يحتوي على FFmpeg. للتحقق:

```bash
ffmpeg -version
```

إذا لم يكن موجوداً:

### الطريقة 1: استخدام Nix (موصى به)

أنشئ ملف `replit.nix`:

```nix
{ pkgs }: {
  deps = [
    pkgs.ffmpeg
    pkgs.python310
  ];
}
```

### الطريقة 2: تثبيت يدوي

```bash
# في Replit Shell
curl -L https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz -o ffmpeg.tar.xz
tar -xf ffmpeg.tar.xz
export PATH=$PATH:$(pwd)/ffmpeg-master-latest-linux64-gpl/bin
```

## الخطوة 5: إعداد API Keys / Step 5: Setup API Keys

### في Replit Secrets

1. انقر على أيقونة القفل 🔒 في الشريط الجانبي
2. أضف Secret جديد:
   - **Key:** `OPENAI_API_KEY`
   - **Value:** مفتاح OpenAI API الخاص بك

### أو استخدام ملف .env

أنشئ ملف `.env`:

```env
OPENAI_API_KEY=your_key_here
```

**تحذير:** لا ترفع ملف `.env` إلى GitHub!

## الخطوة 6: تعديل التكوين / Step 6: Configure

افتح `config.yaml` وعدّل حسب الحاجة:

```yaml
# للاستخدام على Replit، قد ترغب في:
transcription:
  provider: "openai"  # استخدم API بدلاً من المحلي لتوفير الذاكرة
  model: "whisper-1"

highlights:
  default_count: 5
  llm_model: "gpt-4o-mini"  # أرخص من gpt-4
```

## الخطوة 7: تشغيل / Step 7: Run

### مثال 1: معالجة ملف واحد

```bash
python run.py --input media/video.mp4 --n-highlights 5
```

### مثال 2: معالجة مجلد

```bash
python run.py --input media/ --out outputs --n-highlights 3
```

### مثال 3: مع اللغة العربية

```bash
python run.py --input media/podcast.mp3 --lang ar --n-highlights 5
```

## الخطوة 8: عرض النتائج / Step 8: View Results

1. انتظر حتى تنتهي المعالجة
2. افتح مجلد `outputs/`
3. ستجد مجلد لكل ملف معالَج
4. داخل كل مجلد: مجلدات `highlight_01/`, `highlight_02/`, إلخ

## نصائح لـ Replit / Replit Tips

### 1. توفير الذاكرة

- استخدم `local_model: "tiny"` أو `"base"` للنسخ المحلي
- استخدم `gpt-4o-mini` بدلاً من `gpt-4`
- عطّل المعالجة المتوازية

### 2. تسريع المعالجة

- استخدم OpenAI API بدلاً من Whisper المحلي
- استخدم `preset: "veryfast"` للفيديو
- قلل `crf` إلى 26-28

### 3. التعامل مع الملفات الكبيرة

- قسم الملفات الكبيرة إلى أجزاء أصغر أولاً
- استخدم صيغ مضغوطة (MP3 بدلاً من WAV)
- قلل دقة الفيديو في `config.yaml`

### 4. حفظ المخرجات

- Replit يحذف الملفات بعد فترة من عدم الاستخدام
- حمّل المخرجات المهمة إلى Google Drive أو Dropbox
- أو استخدم Replit Database

## استكشاف الأخطاء على Replit / Troubleshooting on Replit

### خطأ: Out of memory

**الحل:**
```yaml
# في config.yaml
transcription:
  provider: "openai"  # استخدم API بدلاً من المحلي
  local_model: "tiny"  # إذا استخدمت المحلي

highlights:
  llm_model: "gpt-4o-mini"  # استخدم نموذج أصغر
```

### خطأ: FFmpeg not found

**الحل:**
- أضف `replit.nix` كما هو موضح أعلاه
- أو استخدم الطريقة اليدوية

### خطأ: Timeout

**الحل:**
- Replit له حد زمني للعمليات
- قسم الملفات الكبيرة
- استخدم Keep-Alive في Replit

### خطأ: API rate limit

**الحل:**
- أضف تأخير بين الطلبات
- استخدم خطة OpenAI أعلى
- قلل عدد النقاط المهمة

## مثال كامل / Complete Example

```bash
# 1. تثبيت المتطلبات
pip install -r requirements.txt

# 2. التحقق من FFmpeg
ffmpeg -version

# 3. تشغيل المعالجة
python run.py \
  --input media/podcast_episode_01.mp3 \
  --out outputs \
  --n-highlights 5 \
  --lang ar

# 4. عرض النتائج
ls -la outputs/podcast_episode_01/
```

## روابط مفيدة / Useful Links

- [Replit Documentation](https://docs.replit.com)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)

---

**ملاحظة:** Replit قد يكون أبطأ من الخادم المحلي بسبب الموارد المحدودة. للمعالجة الكبيرة، فكر في استخدام خادم مخصص أو Replit Deploy.

**Note:** Replit may be slower than local server due to limited resources. For large-scale processing, consider using a dedicated server or Replit Deploy.

