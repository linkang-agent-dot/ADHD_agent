# GRFal Tool Catalog - Detailed Parameters

Complete parameter reference for all 39 GRFal API tools.

> Call any tool via: `python call_grfal.py --tool <name> --params '<json>' [--file key=path]`

## Image Generation

### generate_image
Text-to-image and image-to-image generation.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| prompt | str | required | Text prompt describing the image |
| reference_images | List[str] | [] | Reference images (URLs or base64). Use `--file reference_images=path` |
| model | str | "gemini" | Model: gemini, gpt, flux, seedream, qwen, wan, runway, vidu, kling, ideogram, hunyuan |
| num_images | int | 2 | Number of images to generate |
| aspect_ratio | str | "1:1" | Aspect ratio (e.g., "16:9", "9:16", "1:1") |

```bash
# Text-to-image
python call_grfal.py --tool generate_image --params "{\"prompt\": \"a cute cat\", \"model\": \"gemini\"}"

# Image-to-image (with reference)
python call_grfal.py --tool generate_image --params "{\"prompt\": \"make it more colorful\"}" --file reference_images=input.png
```

### lora_generation
Generate images using LoRA presets.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| prompt | str | required | Text prompt |
| reference_images | List[str] | [] | Reference images |
| preset | str | required | LoRA preset name |
| model | str | "flux_dev" | Model: flux_dev, flux_pro, qwen, flux2, z_image |
| ref1_type | str | "参考内容" | Reference type for slot 1 |
| ref1_strength | str | "适度" | Reference strength for slot 1 |

### kontext_lora
Kontext style transfer with LoRA presets.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Input images. Use `--file image_paths=path` |
| preset | str | required | Kontext preset (e.g., "Kontext X2风格", "Kontext P2徽章") |

---

## Image Processing

### upscale_image
Image super-resolution.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Images to upscale. Use `--file image_paths=path` |
| model | str | None | Model: SeedVR, Crystal, Topaz, Recraft, Ideogram, Sima, Flux, UltraSharp |
| scale | int | 2 | Upscale factor |

### remove_background
AI background removal.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Images. Use `--file image_paths=path` |
| add_edge | bool | false | Add white edge around subject |

### replace_background
Replace background with AI-generated one.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Images. Use `--file image_paths=path` |
| background_prompt | str | required | Description of new background |
| light_direction | str | "无" | Light direction for compositing |

### image_extend
Outpainting - extend image canvas. Prompt is auto-generated from the image.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Images. Use `--file image_paths=path` |
| ratio | str | "16:9" | Target aspect ratio |

### image_resize
Resize image with transparency support.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Images. Use `--file image_paths=path` |
| width | int | required | Target width in pixels |
| height | int | required | Target height in pixels |

### image_remove_lighting
Remove uneven lighting, restore uniform illumination.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Images. Use `--file image_paths=path` |

### image_group_photo
Multi-character composite photo.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Character images. Use `--file image_paths=path` |
| prompt | str | required | Scene description |

### image_camera_angle
Change camera viewing angle.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Images. Use `--file image_paths=path` |
| horizontal_angle | float | 0 | Horizontal rotation angle |
| vertical_angle | float | 0 | Vertical rotation angle |

### image_keyframe
Generate video keyframes/storyboards.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Reference images. Use `--file image_paths=path` |
| prompt | str | required | Keyframe description |

### image_layered
AI automatic layer separation.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Images to separate. Use `--file image_paths=path` |

### image_split
Split image into sub-images and upscale each.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Images. Use `--file image_paths=path` |

---

## Video Generation

### generate_video
Text-to-video and image-to-video generation.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| prompt | str | required | Video description |
| reference_images | List[str] | [] | Start frame images. Use `--file reference_images=path` |
| model | str | required | Model: seadance, hailuo, veo3, sora, vidu, kling, wan, runway |
| duration | int | varies | Duration in seconds (model-dependent) |

```bash
# Text-to-video
python call_grfal.py --tool generate_video --params "{\"prompt\": \"a cat walking\", \"model\": \"kling\"}" --timeout 600

# Image-to-video
python call_grfal.py --tool generate_video --params "{\"prompt\": \"camera slowly pans\"}" --file reference_images=keyframe.png --timeout 600
```

---

## Video Processing

### video_upscale
Video super-resolution (2x upscale).

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| video_path | str | required | Video file. Use `--file video_path=path` |
| model | str | varies | Upscale model |

### video_modify
Modify video style or elements.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| video_path | str | required | Video file. Use `--file video_path=path` |
| prompt | str | required | Modification description |
| model | str | varies | Model to use |

### video_to_audio
Generate audio/soundtrack for video.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| video_path | str | required | Video file. Use `--file video_path=path` |
| prompt | str | "" | Audio description |

### video_lipsync
Synchronize lip movements with audio.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| video_path | str | required | Video file. Use `--file video_path=path` |
| audio_path | str | required | Audio file. Use `--file audio_path=path` |
| sync_mode | str | "latentsync" | `latentsync`=高质量(慢), `lipsync`=快速(质量稍低) |

### video_portrait
Video-driven character animation / motion transfer.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_path | str | required | Character image (single). Use `--file image_path=path` |
| video_path | str | required | Driving video. Use `--file video_path=path` |
| portrait_mode | str | required | `视频替换角色`=用图片替换视频中的人物, `视频动作驱动图片`=用视频动作驱动静态图片 |

### video_avatar
Audio-driven avatar animation. Generates a talking video by driving a character image with audio.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_path | str | required | Character image (single). Use `--file image_path=path` |
| audio_path | str | required | Audio file (mp3/wav). Use `--file audio_path=path` |
| prompt | str | "" | Optional video description |

### video_reframe
Change video aspect ratio.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| video_path | str | required | Video file. Use `--file video_path=path` |
| target_ratio | str | required | Target: 16:9, 9:16, 1:1, 4:3, 3:4 |

### video_remove_background
Remove video background.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| video_path | str | required | Video file. Use `--file video_path=path` |

### video_speed
Change video playback speed.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| video_path | str | required | Video file. Use `--file video_path=path` |
| speed | float | required | Speed multiplier: 0.25 to 4.0 (1.0 = original, >1 faster, <1 slower) |

### export_sbs_video
Export side-by-side transparent video (for Unity).

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| input_videos | List[str] | required | Videos to export. Use `--file input_videos=path` |
| quality | int | required | Output quality |

---

## Utility & Special

### virtual_tryon
Virtual clothes try-on.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| model_image | str | required | Model/person image. Use `--file model_image=path` |
| garment_image | str | required | Garment image. Use `--file garment_image=path` |

### describe_media
Describe image or video content using AI. Returns a text description.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| media_path | str | required | Image or video. Use `--file media_path=path` |
| media_type | str | "auto" | Force type: auto, image, video |

### synthesize_card
Card compositing (content + frame overlay). Uses @batch_image_process decorator.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| content_image_path | str | required | Content image. Use `--file content_image_path=path` (or image_paths for batch) |
| frame_image_path | str | required | Frame image (with transparent holes). Use `--file frame_image_path=path` |

### correct_yellow_tint
Fix yellow color cast in images.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Images. Use `--file image_paths=path` |
| strength | int | required | Correction strength |
| red_adj | int | required | Red channel adjustment |
| green_adj | int | required | Green channel adjustment |
| blue_adj | int | required | Blue channel adjustment |
| saturation_adj | int | required | Saturation adjustment |

### vector_generation
Generate vector graphics (SVG).

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| prompt | str | required | Description |
| jfile | str | required | Template name |
| size | str | required | Output size |

### screenshot_localization
Multi-language screenshot localization.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| image_paths | List[str] | required | Screenshots. Use `--file image_paths=path` |
| languages | List[str] | required | Language codes: ru-RU, en-US, fr-FR, de-DE, id, it-IT, pt-PT, es-ES, ja-JP, ko-KR, zh-TW, ar-SA, tr-TR, vi-VN, th-TH, pt-BR, es-MX, ms-MY, hi-IN, zh-HK, fil-PH |
| platform | str | required | Platform: android, ios, ipad |
| extra_prompt | str | "" | Additional localization instructions |

### pdf_enhancement
PDF text clarity enhancement (via Gemini).

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| pdf_file | str | required | PDF file. Use `--file pdf_file=path` |
| custom_prompt | str | None | Custom enhancement prompt |
| max_concurrency | int | 4 | Max parallel processing |

### pdf_compression
Compress PDF file size.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| pdf_file | str | required | PDF file. Use `--file pdf_file=path` |
| image_quality | int | 75 | Image quality (1-100) |
| compress_images | bool | true | Whether to compress images |
| max_image_size | int | None | Max image dimension in pixels |
| remove_metadata | bool | true | Remove metadata |

---

## 3D & Training

### generate_3d
3D model generation from text or image.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| prompt | str | "" | Text description (for text-to-3D) |
| image_paths | List[str] | [] | Reference images (for image-to-3D). Use `--file image_paths=path` |
| model | str | required | Model: hunyuan, rodin, meshy, tripo, trellis |
| face_limit | int | varies | Max face count for mesh |

### reduce_face
Reduce 3D model face/polygon count (uses Tencent Hunyuan 3D).

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| model_file | str | required | 3D model file (GLB/OBJ). Use `--file model_file=path` |

### train_model
LoRA model training.

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| zip_file | str | required | Training data ZIP. Use `--file zip_file=path` |
| mode | str | required | Training mode |
| trigger_word | str | "" | LoRA trigger word |

---

## Creative Workflows

### creative_workflow
End-to-end creative pipeline (character design, PPT, etc.).

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| user_input | str | required | Creative brief/instructions |
| tool_id | str | "ppt_generation" | Workflow: p2_fighter_design, x2_hero_design, p2_festival_design, p2_carrier_design, p2_mech_design, p2_mech_skin_design, ppt_generation |
| reference_files | List[str] | [] | Reference files. Use `--file reference_files=path` |

```bash
python call_grfal.py --tool creative_workflow --params "{\"user_input\": \"design a sci-fi mech\", \"tool_id\": \"p2_mech_design\"}" --timeout 600
```
