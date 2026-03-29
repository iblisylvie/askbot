# HTML 组件库

> 生成 HTML 时复用以下 CSS + 组件，只替换内容，不要重写框架。

---

## 页面骨架

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>小红书轮播图 - [主题]</title>
<style>
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: #111;
    display: flex; flex-direction: column; align-items: center;
    padding-top: 70px; padding-bottom: 80px;
    font-family: -apple-system, 'PingFang SC', 'Microsoft YaHei', sans-serif;
  }
  .slide {
    width: 540px; height: 720px;
    position: relative; overflow: hidden;
    border-radius: 8px; margin-bottom: 40px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.5);
  }
  /* 暗底 */
  .bg-dark { position: absolute; inset: 0; background: VAR_PRIMARY; }
  .bg-dark::after {
    content: ''; position: absolute; inset: 0;
    background:
      radial-gradient(circle at 80% 15%, rgba(255,255,255,0.03) 0%, transparent 50%),
      radial-gradient(circle at 20% 85%, rgba(0,0,0,0.08) 0%, transparent 50%);
  }
  /* 浅底 */
  .bg-light { position: absolute; inset: 0; background: VAR_LIGHT; }
  /* 深黑底（结尾专用） */
  .bg-deep { position: absolute; inset: 0; background: #0F1F18; }

  .content { position: absolute; inset: 0; padding: 28px; display: flex; flex-direction: column; z-index: 2; }

  /* 品牌角标 */
  .brand-tag {
    position: absolute; top: 22px; left: 28px;
    display: flex; align-items: center; gap: 8px; z-index: 3;
  }
  .brand-tag svg { width: 22px; height: 22px; }
  .brand-tag span { font-size: 12px; font-weight: 600; letter-spacing: 1px; }
  .brand-tag.on-dark span { color: rgba(255,255,255,0.45); }
  .brand-tag.on-light span { color: rgba(26,51,40,0.35); }

  /* 页码 */
  .page-num { position: absolute; bottom: 22px; right: 28px; font-size: 12px; z-index: 3; }
  .page-num.on-dark { color: rgba(255,255,255,0.18); }
  .page-num.on-light { color: rgba(26,51,40,0.18); }

  /* 下载工具栏 */
  .toolbar {
    position: fixed; top: 0; left: 0; right: 0; z-index: 100;
    background: rgba(17,17,17,0.95); backdrop-filter: blur(10px);
    border-bottom: 1px solid rgba(255,255,255,0.08);
    padding: 12px 20px; display: flex; align-items: center;
    justify-content: center; gap: 12px;
  }
  .toolbar .btn {
    background: VAR_PRIMARY; color: VAR_LIGHT; border: none;
    padding: 9px 22px; border-radius: 7px; font-size: 14px;
    font-weight: 600; cursor: pointer;
  }
  .toolbar .btn.red { background: VAR_ACCENT; }
  .toolbar .progress { font-size: 13px; color: rgba(255,255,255,0.4); min-width: 100px; }
</style>
</head>
<body>

<div class="toolbar">
  <button class="btn red" onclick="downloadAll()">⬇ 全部下载 ZIP</button>
  <button class="btn" onclick="downloadCurrent()">下载当前</button>
  <span class="progress" id="progress">共 N 张</span>
</div>

<!-- 幻灯片区域 -->
[SLIDES]

<script src="https://cdn.jsdelivr.net/npm/html2canvas@1.4.1/dist/html2canvas.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/jszip@3.10.1/dist/jszip.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/file-saver@2.0.5/dist/FileSaver.min.js"></script>
<script>
const SCALE = 2;
const TITLE = '[主题名]';
async function renderSlide(s) {
  return html2canvas(s, { scale: SCALE, useCORS: true, backgroundColor: null, width: 540, height: 720, logging: false });
}
function toBlob(c) { return new Promise(r => c.toBlob(r, 'image/png')); }
async function downloadAll() {
  const slides = document.querySelectorAll('.slide');
  const p = document.getElementById('progress');
  const zip = new JSZip();
  for (let i = 0; i < slides.length; i++) {
    p.textContent = `渲染 ${i+1}/${slides.length}...`;
    zip.file(`${TITLE}-${String(i+1).padStart(2,'0')}.png`, await toBlob(await renderSlide(slides[i])));
  }
  p.textContent = '打包中...';
  saveAs(await zip.generateAsync({type:'blob'}), `${TITLE}-小红书.zip`);
  p.textContent = `✓ ${slides.length} 张已下载`;
}
async function downloadCurrent() {
  const slides = document.querySelectorAll('.slide');
  const vc = window.innerHeight / 2;
  let idx = 0, min = Infinity;
  slides.forEach((s, i) => { const d = Math.abs(s.getBoundingClientRect().top + 360 - vc); if (d < min) { min = d; idx = i; } });
  const p = document.getElementById('progress');
  p.textContent = '渲染中...';
  saveAs(await toBlob(await renderSlide(slides[idx])), `${TITLE}-${String(idx+1).padStart(2,'0')}.png`);
  p.textContent = `✓ 第 ${idx+1} 张已下载`;
}
</script>
</body>
</html>
```

> **变量替换说明：**
> - `VAR_PRIMARY` → 品牌暗底色（默认 `#1A3328`）
> - `VAR_LIGHT` → 品牌浅底色（默认 `#F2EDE3`）
> - `VAR_ACCENT` → 强调色（默认 `#C44536`）
> - `[主题名]` → 下载文件名前缀
> - `N` → 总幻灯片数

---

## 品牌角标 SVG

**暗底版（class="brand-tag on-dark"）：**
```html
<div class="brand-tag on-dark">
  <svg viewBox="0 0 32 32" fill="none">
    <defs>
      <linearGradient id="spiralGradDark" x1="50%" y1="50%" x2="100%" y2="0%">
        <stop offset="0%" style="stop-color:VAR_ACCENT"/>
        <stop offset="100%" style="stop-color:VAR_ACCENT;stop-opacity:0.75"/>
      </linearGradient>
    </defs>
    <path d="M 16 16 Q 17 15 18 15 Q 19 15 19.5 16 Q 20 17 19 18.5 Q 17.5 19.5 16 19.5 Q 13.5 19.5 12 18 Q 10.5 16.5 10.5 14 Q 10.5 11 12.5 9 Q 14.5 7 17.5 7 Q 21.5 7 24 9.5 Q 26.5 12 26.5 16 Q 26.5 21 23 24.5 Q 19 28 14 28"
          stroke="url(#spiralGradDark)" stroke-width="1.8" fill="none" stroke-linecap="round"/>
    <circle cx="16" cy="16" r="2" fill="VAR_ACCENT"/>
    <circle cx="19" cy="18.5" r="1.2" fill="VAR_ACCENT" opacity="0.8"/>
    <circle cx="12" cy="18" r="1" fill="VAR_ACCENT" opacity="0.7"/>
    <circle cx="12.5" cy="9" r="0.8" fill="VAR_ACCENT" opacity="0.6"/>
    <circle cx="24" cy="9.5" r="0.7" fill="VAR_ACCENT" opacity="0.5"/>
  </svg>
  <span>[品牌名]</span>
</div>
```

**浅底版（class="brand-tag on-light"）：**
```html
<div class="brand-tag on-light">
  <svg viewBox="0 0 32 32" fill="none">
    <defs>
      <linearGradient id="spiralGradLight" x1="50%" y1="50%" x2="100%" y2="0%">
        <stop offset="0%" style="stop-color:VAR_ACCENT"/>
        <stop offset="100%" style="stop-color:VAR_ACCENT;stop-opacity:0.75"/>
      </linearGradient>
    </defs>
    <path d="M 16 16 Q 17 15 18 15 Q 19 15 19.5 16 Q 20 17 19 18.5 Q 17.5 19.5 16 19.5 Q 13.5 19.5 12 18 Q 10.5 16.5 10.5 14 Q 10.5 11 12.5 9 Q 14.5 7 17.5 7 Q 21.5 7 24 9.5 Q 26.5 12 26.5 16 Q 26.5 21 23 24.5 Q 19 28 14 28"
          stroke="url(#spiralGradLight)" stroke-width="1.8" fill="none" stroke-linecap="round"/>
    <circle cx="16" cy="16" r="2" fill="VAR_ACCENT"/>
    <circle cx="19" cy="18.5" r="1.2" fill="VAR_ACCENT" opacity="0.8"/>
    <circle cx="12" cy="18" r="1" fill="VAR_ACCENT" opacity="0.7"/>
    <circle cx="12.5" cy="9" r="0.8" fill="VAR_ACCENT" opacity="0.6"/>
    <circle cx="24" cy="9.5" r="0.7" fill="VAR_ACCENT" opacity="0.5"/>
  </svg>
  <span>[品牌名]</span>
</div>
```

> 如果品牌名为空，省略 `<span>` 标签。

---

## 幻灯片模板

### Cover — 封面

```html
<div class="slide">
  <div class="bg-dark"></div>
  [BRAND_TAG_DARK]
  <div class="page-num on-dark">1/N</div>
  <div class="content" style="justify-content:center; padding: 48px 40px;">
    <div style="font-size:12px;color:VAR_ACCENT;letter-spacing:3px;font-weight:700;margin-bottom:18px;text-align:center;">[日期/来源标签]</div>
    <div style="font-size:48px;font-weight:900;color:VAR_LIGHT;line-height:1.2;text-align:center;margin-bottom:8px;">[大标题]</div>
    <div style="font-size:20px;font-weight:500;color:rgba(242,237,227,0.45);text-align:center;margin-bottom:0;">[副标题]</div>
    <div style="width:48px;height:3px;background:VAR_ACCENT;border-radius:2px;margin:22px auto;"></div>
    <!-- 摘要列表，每条一行 -->
    <div style="display:flex;flex-direction:column;gap:8px;">
      <div style="display:flex;align-items:center;gap:12px;padding:9px 13px;border-radius:7px;background:rgba(255,255,255,0.05);">
        <span style="font-size:16px;">[emoji]</span>
        <span style="font-size:13px;color:rgba(255,255,255,0.75);">[一句话摘要]</span>
      </div>
      <!-- 重复若干条 -->
    </div>
    <!-- 可选：底部数字锚点 -->
    <div style="margin-top:16px;padding:10px 14px;border:1px solid rgba(196,69,54,0.3);border-radius:7px;text-align:center;background:rgba(196,69,54,0.07);">
      <span style="font-size:11px;color:rgba(255,255,255,0.35);letter-spacing:2px;">今日最大的数字</span><br>
      <span style="font-size:20px;font-weight:900;color:VAR_ACCENT;">[数字]</span>
      <span style="font-size:13px;color:rgba(255,255,255,0.45);"> [单位/说明]</span>
    </div>
  </div>
</div>
```

---

### Numbers — 数字炸弹

```html
<div class="slide">
  <div class="bg-light"></div>
  [BRAND_TAG_LIGHT]
  <div class="page-num on-light">N/总N</div>
  <div class="content" style="padding-top:58px;">
    <div style="font-size:11px;color:VAR_ACCENT;letter-spacing:2px;font-weight:700;margin-bottom:7px;">[小标签]</div>
    <div style="font-size:26px;font-weight:900;color:VAR_PRIMARY;line-height:1.3;margin-bottom:4px;">[标题]</div>
    <div style="font-size:13px;color:#7A8C80;margin-bottom:18px;">[副标题/来源说明]</div>
    <!-- 2x2 数字网格 -->
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:16px;">
      <div style="background:VAR_PRIMARY;border-radius:11px;padding:17px 13px;">
        <div style="font-size:38px;font-weight:900;color:VAR_ACCENT;line-height:1;">[数字]</div>
        <div style="font-size:11px;color:rgba(242,237,227,0.45);margin-top:5px;">[名称/单位]</div>
        <div style="font-size:10px;color:rgba(242,237,227,0.28);margin-top:2px;">[补充说明]</div>
      </div>
      <!-- 重复 3 个 -->
    </div>
    <!-- 底部说明框（可选） -->
    <div style="background:rgba(26,51,40,0.06);border-radius:9px;padding:13px 15px;">
      <div style="font-size:12px;font-weight:700;color:VAR_PRIMARY;margin-bottom:7px;">[框标题]</div>
      <div style="font-size:12px;color:#555;line-height:1.8;">[说明内容，可用 emoji 前缀]</div>
    </div>
  </div>
</div>
```

---

### Timeline — 时间线/流程

```html
<div class="slide">
  <div class="bg-dark"></div>
  [BRAND_TAG_DARK]
  <div class="page-num on-dark">N/总N</div>
  <div class="content" style="padding-top:58px;">
    <div style="font-size:11px;color:VAR_ACCENT;letter-spacing:2px;font-weight:700;margin-bottom:7px;">[小标签]</div>
    <div style="font-size:24px;font-weight:900;color:VAR_LIGHT;line-height:1.3;margin-bottom:18px;">[标题]</div>
    <!-- 时间线节点，最多 4-5 个 -->
    <div style="display:flex;gap:13px;margin-bottom:0;">
      <div style="display:flex;flex-direction:column;align-items:center;">
        <div style="width:27px;height:27px;border-radius:50%;background:VAR_ACCENT;color:VAR_LIGHT;font-size:13px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;">1</div>
        <div style="width:2px;flex:1;background:rgba(255,255,255,0.07);min-height:28px;"></div>
      </div>
      <div style="padding-top:3px;padding-bottom:14px;">
        <div style="font-size:14px;font-weight:700;color:VAR_LIGHT;">[事件标题]</div>
        <div style="font-size:12px;color:rgba(255,255,255,0.45);line-height:1.6;margin-top:3px;">[细节说明，关键词用 <span style="color:VAR_ACCENT;font-weight:700"> 高亮]</span></div>
      </div>
    </div>
    <!-- 最后一个节点不需要连接线，圆圈改为带边框的样式 -->
    <div style="display:flex;gap:13px;">
      <div style="width:27px;height:27px;border-radius:50%;background:rgba(196,69,54,0.25);border:1px solid VAR_ACCENT;color:VAR_ACCENT;font-size:13px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0;">+</div>
      <div style="padding-top:3px;">
        <div style="font-size:14px;font-weight:700;color:VAR_LIGHT;">[最后节点标题]</div>
        <div style="font-size:12px;color:rgba(255,255,255,0.45);line-height:1.6;margin-top:3px;">[内容]</div>
      </div>
    </div>
  </div>
</div>
```

---

### Comparison — 对比表

```html
<div class="slide">
  <div class="bg-light"></div>
  [BRAND_TAG_LIGHT]
  <div class="page-num on-light">N/总N</div>
  <div class="content" style="padding-top:58px;">
    <div style="font-size:11px;color:VAR_ACCENT;letter-spacing:2px;font-weight:700;margin-bottom:7px;">[小标签]</div>
    <div style="font-size:26px;font-weight:900;color:VAR_PRIMARY;line-height:1.3;margin-bottom:4px;">[标题]</div>
    <div style="font-size:13px;color:#7A8C80;margin-bottom:18px;">[副标题]</div>
    <!-- 对比对象列表 -->
    <div style="display:flex;flex-direction:column;gap:9px;margin-bottom:18px;">
      <div style="display:flex;align-items:center;justify-content:space-between;padding:13px 17px;background:VAR_PRIMARY;border-radius:9px;">
        <div>
          <div style="font-size:15px;font-weight:800;color:VAR_LIGHT;">[对象名] [emoji]</div>
          <div style="font-size:11px;color:rgba(242,237,227,0.38);margin-top:2px;">[归属/说明]</div>
        </div>
        <!-- 可选状态标签 -->
        <div style="font-size:11px;color:VAR_ACCENT;font-weight:700;background:rgba(196,69,54,0.15);padding:3px 10px;border-radius:20px;">[状态]</div>
      </div>
      <!-- 重复若干个 -->
    </div>
    <!-- 注意事项（可选） -->
    <div style="border-left:3px solid VAR_ACCENT;padding:11px 15px;background:rgba(26,51,40,0.06);border-radius:0 7px 7px 0;">
      <div style="font-size:12px;font-weight:700;color:VAR_PRIMARY;margin-bottom:3px;">⚠️ 注意</div>
      <div style="font-size:12px;color:#555;line-height:1.7;">[注意说明]</div>
    </div>
  </div>
</div>
```

---

### List — 要点列表

```html
<div class="slide">
  <div class="bg-dark"></div>
  [BRAND_TAG_DARK]
  <div class="page-num on-dark">N/总N</div>
  <div class="content" style="padding-top:58px;">
    <div style="font-size:11px;color:VAR_ACCENT;letter-spacing:2px;font-weight:700;margin-bottom:7px;">[小标签]</div>
    <div style="font-size:24px;font-weight:900;color:VAR_LIGHT;line-height:1.3;margin-bottom:18px;">[标题]</div>
    <div style="display:flex;flex-direction:column;gap:7px;">
      <div style="display:flex;align-items:flex-start;padding:11px 13px;border-radius:7px;background:rgba(255,255,255,0.05);gap:11px;">
        <span style="font-size:15px;flex-shrink:0;">[emoji]</span>
        <div>
          <span style="font-size:13px;font-weight:700;color:VAR_LIGHT;">[粗体标题]</span>
          <div style="font-size:11px;color:rgba(255,255,255,0.42);margin-top:3px;line-height:1.6;">[细节说明]</div>
        </div>
      </div>
      <!-- 重复若干条 -->
    </div>
  </div>
</div>
```

---

### Mixed — 数字 + 说明

```html
<div class="slide">
  <div class="bg-light"></div>
  [BRAND_TAG_LIGHT]
  <div class="page-num on-light">N/总N</div>
  <div class="content" style="padding-top:58px;">
    <div style="font-size:11px;color:VAR_ACCENT;letter-spacing:2px;font-weight:700;margin-bottom:7px;">[小标签]</div>
    <div style="font-size:24px;font-weight:900;color:VAR_PRIMARY;line-height:1.3;margin-bottom:18px;">[标题]</div>
    <!-- 数字对比行 -->
    <div style="display:flex;gap:10px;margin-bottom:16px;">
      <div style="flex:1;background:VAR_PRIMARY;border-radius:9px;padding:15px;text-align:center;">
        <div style="font-size:11px;color:rgba(242,237,227,0.38);margin-bottom:5px;">[左标签]</div>
        <div style="font-size:34px;font-weight:900;color:VAR_ACCENT;">[左数字]</div>
        <div style="font-size:11px;color:rgba(242,237,227,0.45);">[左单位]</div>
      </div>
      <div style="display:flex;align-items:center;color:#9BA8A0;font-size:18px;">→</div>
      <div style="flex:1;background:VAR_PRIMARY;border-radius:9px;padding:15px;text-align:center;">
        <div style="font-size:11px;color:rgba(242,237,227,0.38);margin-bottom:5px;">[右标签]</div>
        <div style="font-size:34px;font-weight:900;color:VAR_ACCENT;">[右数字]</div>
        <div style="font-size:11px;color:rgba(242,237,227,0.45);">[右单位]</div>
      </div>
    </div>
    <!-- 详情 key-value 框 -->
    <div style="background:rgba(26,51,40,0.06);border-radius:9px;padding:13px 15px;margin-bottom:13px;">
      <div style="font-size:12px;font-weight:700;color:VAR_PRIMARY;margin-bottom:8px;">[框标题]</div>
      <div style="display:flex;flex-direction:column;gap:5px;">
        <div style="display:flex;justify-content:space-between;">
          <span style="font-size:12px;color:#7A8C80;">[键]</span>
          <span style="font-size:12px;font-weight:700;color:VAR_PRIMARY;">[值]</span>
        </div>
        <!-- 重复若干行 -->
      </div>
    </div>
    <!-- 底部引用块 -->
    <div style="border-left:3px solid VAR_ACCENT;padding:9px 13px;background:rgba(196,69,54,0.06);border-radius:0 7px 7px 0;">
      <div style="font-size:12px;color:#555;line-height:1.7;">[引用内容，关键词用 <strong style="color:VAR_ACCENT"> 高亮</strong>]</div>
    </div>
  </div>
</div>
```

---

### Quote — 结尾卡

```html
<div class="slide">
  <div class="bg-deep"></div>
  [BRAND_TAG_DARK]
  <div class="page-num on-dark">N/N</div>
  <div class="content" style="justify-content:center;align-items:center;text-align:center;padding:48px 40px;">
    <div style="width:40px;height:3px;background:VAR_ACCENT;border-radius:2px;margin:0 auto 28px;"></div>
    <div style="font-size:13px;color:rgba(255,255,255,0.35);letter-spacing:2px;margin-bottom:14px;">[小标语，如"今日最值得记住的"]</div>
    <div style="font-size:22px;font-weight:800;color:VAR_LIGHT;line-height:1.6;margin-bottom:28px;">"[核心金句]"</div>
    <div style="width:40px;height:1px;background:rgba(255,255,255,0.12);margin:0 auto 28px;"></div>
    <!-- 关键词标签 -->
    <div style="display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin-bottom:32px;">
      <div style="padding:7px 14px;border:1px solid rgba(196,69,54,0.4);border-radius:20px;font-size:12px;color:VAR_ACCENT;font-weight:600;">[关键词1]</div>
      <div style="padding:7px 14px;border:1px solid rgba(255,255,255,0.12);border-radius:20px;font-size:12px;color:rgba(255,255,255,0.45);">[关键词2]</div>
      <div style="padding:7px 14px;border:1px solid rgba(255,255,255,0.12);border-radius:20px;font-size:12px;color:rgba(255,255,255,0.45);">[关键词3]</div>
    </div>
    <div style="font-size:12px;color:rgba(255,255,255,0.2);letter-spacing:3px;">[日期/来源]</div>
    <div style="font-size:11px;color:rgba(255,255,255,0.12);margin-top:7px;">[保存提示，如"保存这张图备用"]</div>
  </div>
</div>
```

---

## 暗底/浅底交替规则

| 张序 | 背景 | 品牌角标 class | 页码 class |
|------|------|---------------|------------|
| 1（封面）| bg-dark | on-dark | on-dark |
| 2 | bg-light | on-light | on-light |
| 3 | bg-dark | on-dark | on-dark |
| 4 | bg-light | on-light | on-light |
| ... | 交替 | 对应 | 对应 |
| 最后（结尾）| bg-deep | on-dark | on-dark |
