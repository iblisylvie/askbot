# anyseek icon design — TODO

## 待补资产

- [ ] **横版深色版**：`anyseek_logo_v2_horizontal_mono_white.svg`，用于深色主题网站 header / 邮件深色签名
- [ ] **方版组合标**：mark + "anyseek" 字标垂直堆叠，用于视频片头、icon grid、播客封面
- [ ] **PNG 批量导出脚本**：从 SVG 输出常用尺寸（1024 / 512 / 200 / 64 / 32 / 16 px），脚本放 `scripts/svg_to_png.py`
- [ ] **字体决策**：当前 wordmark 用 `Inter, Helvetica Neue, PingFang SC, Arial` 兜底栈。正式定稿需要选一款品牌字体并转 path（avoid 终端缺字体导致字标走形）

## 待补文档

- [ ] **品牌色规范**：主色 `#E07A5F` 的 HSL / RGB / CMYK / Pantone 近似值；可用辅助色范围；禁止用法
- [ ] **最小尺寸与安全间距**：每个变体的最小可用 px；周围 clearspace 规则
- [ ] **错用示例**：列出常见错误（拉伸变形、改色、加阴影、改背景等）

## 待验证

- [ ] 小红书头像（200×200）真机预览，确认 compact 版本节点可见
- [ ] 微信公众号 banner（2.35:1）真机预览，确认 horizontal 版本居中比例
- [ ] favicon (16/32px) 在 Chrome / Safari tab 中的实际渲染（mini 版是否还能识别为螺旋）
- [ ] 黑底场景（深色 PPT 模板）验证 mono_white 与主版 coral 哪个更合适

## 已完成（v2，2026-05-13）

- [x] 主版 `anyseek_logo_v2_20260513.svg`
- [x] 紧凑版 `anyseek_logo_v2_compact_20260513.svg`
- [x] 纯 mark `anyseek_logo_v2_mark_20260513.svg`
- [x] Favicon `anyseek_logo_v2_mini_20260513.svg`
- [x] 单色黑 `anyseek_logo_v2_mono_black_20260513.svg`
- [x] 单色白 `anyseek_logo_v2_mono_white_20260513.svg`
- [x] 横版组合标 `anyseek_logo_v2_horizontal_20260513.svg`
