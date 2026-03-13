const fs = require('fs');
const path = require('path');

// 检查依赖是否已安装
try {
    var TurndownService = require('turndown');
} catch (e) {
    console.error('错误：未找到 turndown 依赖');
    console.error('');
    console.error('请先在 skill 目录下安装依赖：');
    const skillHome = process.env.AI_WEEKLY_WRITER_HOME || path.join(process.env.HOME, '.claude/skills/ai-weekly-writer');
    console.error(`  cd ${skillHome}`);
    console.error('  npm install');
    console.error('');
    console.error('如需设置环境变量，请添加以下内容到 ~/.bashrc 或 ~/.zshrc：');
    console.error(`  export AI_WEEKLY_WRITER_HOME="${skillHome}"`);
    process.exit(1);
}

// 创建 turndown 实例
const turndownService = new TurndownService({
    headingStyle: 'atx',
    bulletListMarker: '-',
    codeBlockStyle: 'fenced'
});

// 移除不需要的标签，但保留内容
turndownService.remove(['script', 'style', 'link', 'meta', 'iframe', 'noscript', 'head']);

// 获取命令行参数
const inputFile = process.argv[2];

if (!inputFile) {
    console.error('用法: node html2md.js <input.html> [output.md]');
    console.error('');
    console.error('环境变量设置（推荐）：');
    console.error('  export AI_WEEKLY_WRITER_HOME="$HOME/.claude/skills/ai-weekly-writer"');
    console.error('');
    console.error('使用示例：');
    console.error('  node $AI_WEEKLY_WRITER_HOME/scripts/html2md.js input.html');
    process.exit(1);
}

const outputFile = process.argv[3] || inputFile.replace(/\.html?$/i, '.md');

// 读取 HTML 文件
fs.readFile(inputFile, 'utf8', (err, html) => {
    if (err) {
        console.error('读取文件失败:', err.message);
        process.exit(1);
    }

    // 转换为 Markdown
    const markdown = turndownService.turndown(html);

    // 后处理：删除开头的 JavaScript 代码（以 try{ 或 var 或 function 开头的行）
    let cleanedMarkdown = markdown;

    // 删除开头的大段 JS 代码（直到遇到第一个 # 标题）
    const firstHeading = cleanedMarkdown.search(/^# /m);
    if (firstHeading > 0) {
        cleanedMarkdown = cleanedMarkdown.substring(firstHeading);
    }

    // 删除结尾的 JavaScript 代码（从 "window." 或 "function" 或 "[取消]" 开始往后的内容）
    const lastContent = cleanedMarkdown.search(/\nwindow\.[a-z_]+\s*=/);
    const cancelButton = cleanedMarkdown.search(/\n\[取消\]\(javascript:/);
    if (cancelButton > 0) {
        cleanedMarkdown = cleanedMarkdown.substring(0, cancelButton);
    } else if (lastContent > 0) {
        cleanedMarkdown = cleanedMarkdown.substring(0, lastContent);
    }

    // 清理微信 UI 元素
    cleanedMarkdown = cleanedMarkdown
        .replace(/\n{3,}/g, '\n\n')
        .replace(/预览时标签不可点/g, '')
        .replace(/微信扫一扫[\s\S]*?关注该公众号/g, '')
        .replace(/微信扫一扫可打开此内容，[\s\S]*?使用完整服务/g, '')
        .replace(/微信扫一扫[\s\S]*?使用小程序/g, '')
        .replace(/继续滑动看下一个/g, '')
        .replace(/向上滑动看下一个/g, '')
        .replace(/轻触阅读原文/g, '')
        .replace(/Z Potentials/g, '')
        .replace(/\[知道了\]\(javascript:;?\)/g, '')
        .replace(/\[取消\]\(javascript:void\(0\);?\)\s*\[允许\]\(javascript:void\(0\);?\)/g, '')
        .replace(/!\[作者头像\]\([^)]+\)/g, '')
        .replace(/× 分析/g, '')
        .replace(/：\s*，\s*，\s*，\s*，\s*，\s*，\s*，\s*，\s*，\s*，\s*，\s*，\s*。/g, '')
        .replace(/视频 小程序 赞 ，轻点两下取消赞 在看 ，轻点两下取消在看 分享 留言 收藏 听过/g, '')
        .replace(/\[.*?\]\(javascript:void\(0\);?\)/g, '')
        .replace(/在小说阅读器中沉浸阅读/g, '')
        .replace(/\n{3,}/g, '\n\n')
        .trim();

    // 写入 Markdown 文件
    fs.writeFile(outputFile, cleanedMarkdown, 'utf8', (err) => {
        if (err) {
            console.error('写入文件失败:', err.message);
            process.exit(1);
        }
        console.log(`转换成功: ${inputFile} -> ${outputFile}`);
        console.log(`原始 HTML 大小: ${(html.length / 1024).toFixed(2)} KB`);
        console.log(`生成 Markdown 大小: ${(cleanedMarkdown.length / 1024).toFixed(2)} KB`);
    });
});
