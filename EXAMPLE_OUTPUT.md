# مثال على الإخراج المتوقع / Expected Output Example

هذا الملف يوضح هيكل الإخراج المتوقع عند معالجة ملف وسائط.

This file shows the expected output structure when processing a media file.

## مثال: معالجة ملف `podcast_episode_01.mp3`

### هيكل المجلدات / Folder Structure

```
outputs/
└── podcast_episode_01/
    ├── highlights.json
    ├── highlight_01/
    │   ├── clip.mp4
    │   ├── clip_1x1.mp4
    │   ├── clip_9x16.mp4
    │   ├── clip.srt
    │   └── caption.txt
    ├── highlight_02/
    │   ├── clip.mp4
    │   ├── clip_1x1.mp4
    │   ├── clip_9x16.mp4
    │   ├── clip.srt
    │   └── caption.txt
    └── ... (highlight_03, highlight_04, highlight_05)
```

### ملف highlights.json

```json
[
  {
    "start_time": 12.5,
    "end_time": 28.3,
    "hook": "اكتشف كيف يمكن للذكاء الاصطناعي أن يغير مستقبل التعليم",
    "summary": "في هذا الجزء، نناقش التطبيقات العملية للذكاء الاصطناعي في التعليم.\nنستكشف كيف يمكن للتكنولوجيا أن تجعل التعلم أكثر تخصيصاً وفعالية.\nهذا الموضوع مهم جداً للمعلمين والطلاب على حد سواء.",
    "confidence": 0.95,
    "output_folder": "outputs/podcast_episode_01/highlight_01",
    "files": {
      "base_clip": "outputs/podcast_episode_01/highlight_01/clip.mp4",
      "srt": "outputs/podcast_episode_01/highlight_01/clip.srt",
      "resized": {
        "square": "outputs/podcast_episode_01/highlight_01/clip_1x1.mp4",
        "vertical": "outputs/podcast_episode_01/highlight_01/clip_9x16.mp4"
      }
    }
  },
  {
    "start_time": 45.2,
    "end_time": 62.8,
    "hook": "الأسرار الخفية وراء بناء عادات ناجحة",
    "summary": "نتحدث عن العلم وراء تكوين العادات.\nكيف يمكن لأصغر التغييرات أن تحدث أكبر الفروقات.\nنصائح عملية يمكن تطبيقها فوراً.",
    "confidence": 0.92,
    "output_folder": "outputs/podcast_episode_01/highlight_02",
    "files": {
      "base_clip": "outputs/podcast_episode_01/highlight_02/clip.mp4",
      "srt": "outputs/podcast_episode_01/highlight_02/clip.srt",
      "resized": {
        "square": "outputs/podcast_episode_01/highlight_02/clip_1x1.mp4",
        "vertical": "outputs/podcast_episode_01/highlight_02/clip_9x16.mp4"
      }
    }
  }
]
```

### ملف caption.txt (مثال)

```
Caption (Hook):
اكتشف كيف يمكن للذكاء الاصطناعي أن يغير مستقبل التعليم

Summary:
في هذا الجزء، نناقش التطبيقات العملية للذكاء الاصطناعي في التعليم.
نستكشف كيف يمكن للتكنولوجيا أن تجعل التعلم أكثر تخصيصاً وفعالية.
هذا الموضوع مهم جداً للمعلمين والطلاب على حد سواء.
```

### ملف clip.srt (مثال)

```
1
00:00:00,000 --> 00:00:03,500
في هذا الجزء، نناقش التطبيقات العملية

2
00:00:03,500 --> 00:00:07,200
للذكاء الاصطناعي في التعليم.

3
00:00:07,200 --> 00:00:12,800
نستكشف كيف يمكن للتكنولوجيا أن تجعل التعلم

4
00:00:12,800 --> 00:00:15,800
أكثر تخصيصاً وفعالية.
```

## مواصفات الملفات / File Specifications

### ملفات الفيديو / Video Files

- **clip.mp4**: المقطع الأساسي بالحجم الأصلي
- **clip_1x1.mp4**: نسخة مربعة 1080x1080 (مناسب لـ Instagram)
- **clip_9x16.mp4**: نسخة عمودية 1080x1920 (مناسب لـ TikTok, Instagram Reels)

### ملفات النصوص / Text Files

- **caption.txt**: العنوان والملخص بصيغة نصية
- **clip.srt**: ملف ترجمات بصيغة SRT (يمكن استخدامه في أي مشغل فيديو)

### ملف JSON / JSON File

- **highlights.json**: يحتوي على جميع المعلومات عن النقاط المهمة بما في ذلك:
  - الأوقات (timestamps)
  - العناوين والملخصات
  - ثقة النموذج (confidence score)
  - مسارات الملفات

## استخدام الملفات / Using the Files

### رفع على Instagram Reels

استخدم `clip_9x16.mp4` (النسخة العمودية)

### رفع على Instagram Post

استخدم `clip_1x1.mp4` (النسخة المربعة)

### رفع على TikTok

استخدم `clip_9x16.mp4` (النسخة العمودية)

### إضافة ترجمات يدوياً

استخدم `clip.srt` مع أي برنامج تحرير فيديو (Premiere, Final Cut, etc.)

## ملاحظات / Notes

- جميع الملفات تستخدم ترميز H.264 للفيديو و AAC للصوت
- الجودة الافتراضية: CRF 23 (جودة جيدة مع حجم معقول)
- الملفات الصوتية فقط ستنتج فيديو مع موجة صوتية (waveform visualization)

