# هيكل المشروع / Project Structure

هذا الملف يوضح هيكل المشروع ووظيفة كل ملف.

This file explains the project structure and the purpose of each file.

## هيكل الملفات / File Structure

```
media-reels-generator/
│
├── run.py                    # نقطة الدخول الرئيسية - Main entry point
├── utils.py                  # أدوات مساعدة - Utility functions
├── transcribe.py             # نسخ الصوت - Audio transcription
├── highlight.py              # استخراج النقاط المهمة - Highlight extraction
├── editor.py                 # تحرير الفيديو - Video editing
│
├── config.yaml               # ملف التكوين - Configuration file
├── requirements.txt          # متطلبات Python - Python dependencies
│
├── README.md                 # دليل الاستخدام الرئيسي - Main usage guide
├── REPLIT_GUIDE.md          # دليل Replit - Replit usage guide
├── EXAMPLE_OUTPUT.md        # مثال على الإخراج - Output example
├── PROJECT_STRUCTURE.md      # هذا الملف - This file
│
├── .gitignore                # ملفات Git المستثناة - Git ignore file
├── .env.example              # مثال على متغيرات البيئة - Environment variables example
│
└── outputs/                  # مجلد الإخراج (يُنشأ تلقائياً) - Output directory (auto-created)
    └── [original_filename]/
        ├── highlights.json
        └── highlight_XX/
            ├── clip.mp4
            ├── clip_1x1.mp4
            ├── clip_9x16.mp4
            ├── clip.srt
            └── caption.txt
```

## وصف الملفات / File Descriptions

### ملفات Python الرئيسية / Main Python Files

#### `run.py`
- **الوظيفة:** نقطة الدخول الرئيسية للتطبيق
- **Function:** Main entry point for the application
- **المحتوى:**
  - معالجة سطر الأوامر (CLI)
  - تنسيق المعالجة المتوازية
  - استدعاء الوحدات الأخرى
  - عرض ملخص النتائج

#### `utils.py`
- **الوظيفة:** أدوات مساعدة مشتركة
- **Function:** Shared utility functions
- **المحتوى:**
  - إعداد السجلات (logging)
  - تحميل التكوين
  - التعامل مع الملفات
  - التحقق من صحة الملفات
  - إنشاء هيكل الإخراج

#### `transcribe.py`
- **الوظيفة:** نسخ الصوت إلى نص
- **Function:** Transcribe audio to text
- **المحتوى:**
  - دعم مقدمي خدمة متعددين (OpenAI, Whisper المحلي, Hugging Face)
  - كشف اللغة التلقائي
  - معالجة الأخطاء وإعادة المحاولة

#### `highlight.py`
- **الوظيفة:** استخراج النقاط المهمة من النص
- **Function:** Extract highlights from transcript
- **المحتوى:**
  - استخدام LLM (GPT) لتحليل النص
  - تحديد الأوقات المناسبة
  - إنشاء العناوين والملخصات
  - التحقق من صحة النتائج

#### `editor.py`
- **الوظيفة:** تحرير الفيديو والصوت
- **Function:** Video and audio editing
- **المحتوى:**
  - استخراج المقاطع باستخدام FFmpeg
  - تغيير حجم الفيديو
  - إنشاء ملفات SRT
  - حرق الترجمات في الفيديو
  - إنشاء تصورات للملفات الصوتية

### ملفات التكوين / Configuration Files

#### `config.yaml`
- **الوظيفة:** إعدادات التطبيق
- **Function:** Application settings
- **المحتوى:**
  - مفاتيح API
  - إعدادات النسخ
  - إعدادات استخراج النقاط المهمة
  - إعدادات الفيديو
  - إعدادات الإخراج

#### `requirements.txt`
- **الوظيفة:** قائمة مكتبات Python المطلوبة
- **Function:** List of required Python packages
- **المحتوى:**
  - openai
  - whisper
  - langdetect
  - pyyaml
  - ffmpeg-python
  - وغيرها

### ملفات التوثيق / Documentation Files

#### `README.md`
- **الوظيفة:** الدليل الرئيسي للمستخدم
- **Function:** Main user guide
- **المحتوى:**
  - التثبيت
  - الاستخدام
  - التكوين
  - استكشاف الأخطاء

#### `REPLIT_GUIDE.md`
- **الوظيفة:** دليل خاص لاستخدام Replit
- **Function:** Specific guide for Replit usage
- **المحتوى:**
  - خطوات الإعداد على Replit
  - نصائح خاصة بـ Replit
  - استكشاف الأخطاء على Replit

#### `EXAMPLE_OUTPUT.md`
- **الوظيفة:** مثال على هيكل الإخراج
- **Function:** Example of output structure
- **المحتوى:**
  - هيكل المجلدات
  - أمثلة على الملفات
  - مواصفات الملفات

#### `PROJECT_STRUCTURE.md`
- **الوظيفة:** هذا الملف - يوضح هيكل المشروع
- **Function:** This file - explains project structure

### ملفات أخرى / Other Files

#### `.gitignore`
- **الوظيفة:** ملفات Git المستثناة
- **Function:** Git ignored files
- **المحتوى:**
  - ملفات Python المؤقتة
  - مجلدات الإخراج
  - ملفات البيئة (.env)
  - ملفات IDE

#### `.env.example`
- **الوظيفة:** مثال على متغيرات البيئة
- **Function:** Example environment variables
- **المحتوى:**
  - قالب لمفاتيح API
  - تعليمات الإعداد

## تدفق المعالجة / Processing Flow

```
1. run.py
   │
   ├──> utils.py: تحميل التكوين والحصول على الملفات
   │
   ├──> transcribe.py: نسخ الصوت
   │     │
   │     └──> OpenAI API / Local Whisper / Hugging Face
   │
   ├──> highlight.py: استخراج النقاط المهمة
   │     │
   │     └──> OpenAI GPT / Anthropic Claude
   │
   └──> editor.py: تحرير الفيديو
         │
         ├──> استخراج المقاطع
         ├──> تغيير الحجم
         ├──> إنشاء الترجمات
         └──> حرق الترجمات (اختياري)
```

## التبعيات / Dependencies

### مكتبات Python / Python Libraries

- `openai`: للنسخ واستخراج النقاط المهمة
- `whisper`: للنسخ المحلي (اختياري)
- `langdetect`: لكشف اللغة
- `pyyaml`: لقراءة ملفات YAML
- `python-dotenv`: لقراءة ملفات .env
- `ffmpeg-python`: واجهة Python لـ FFmpeg
- `tqdm`: شريط التقدم
- `pydantic`: للتحقق من البيانات

### أدوات خارجية / External Tools

- **FFmpeg**: لتحرير الفيديو والصوت
  - يجب تثبيته في النظام
  - متوفر لجميع المنصات

### APIs خارجية / External APIs

- **OpenAI API**: للنسخ (Whisper) واستخراج النقاط المهمة (GPT)
- **Anthropic API**: بديل لاستخراج النقاط المهمة (اختياري)

## التوسع / Extensibility

### إضافة مقدم خدمة نسخ جديد

1. أنشئ class جديد يرث من `TranscriptionProvider`
2. نفذ دالة `transcribe()`
3. أضف الحالة في `create_transcription_provider()` في `transcribe.py`

### إضافة مقدم خدمة LLM جديد

1. أضف دعم في `HighlightExtractor.__init__()`
2. أضف منطق الاستدعاء في `_call_llm()`
3. حدّث `config.yaml` بالخيارات الجديدة

### إضافة تنسيق إخراج جديد

1. أضف تنسيق جديد في `config.yaml` تحت `video.formats`
2. الكود في `editor.py` سيتعامل معه تلقائياً

## الأمان / Security

- **مفاتيح API**: لا ترفع ملفات `.env` أو `config.yaml` مع المفاتيح إلى Git
- **التحقق**: استخدم `--confirm-copyright` للمحتوى من طرف ثالث
- **السجلات**: راجع `processing.log` للتحقق من العمليات

## الأداء / Performance

- **المعالجة المتوازية**: مفعّلة عبر `--parallel`
- **تحسين الذاكرة**: استخدم نماذج أصغر للنسخ
- **تحسين السرعة**: استخدم `preset: "veryfast"` للفيديو

---

**ملاحظة:** هذا المشروع مصمم ليكون قابلاً للتوسع والتخصيص. لا تتردد في تعديل الكود حسب احتياجاتك.

**Note:** This project is designed to be extensible and customizable. Feel free to modify the code according to your needs.

