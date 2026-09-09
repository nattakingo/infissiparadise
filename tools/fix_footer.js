const fs = require('fs');
const path = require('path');

const rootDir = __dirname + '/..';

const rootFiles = fs.readdirSync(rootDir).filter(f => f.endsWith('.html'));
const blogDir = path.join(rootDir, 'blog');
const blogFiles = fs.readdirSync(blogDir).filter(f => f.endsWith('.html')).map(f => path.join('blog', f));

function detectEol(c) {
    return c.includes('\r\n') ? '\r\n' : '\n';
}

function footerBlock(eol, prefix, label) {
    const href = p => `../${p}`;
    const link = (p, text) => `                        <li><a href="${prefix ? href(p) : p}">${text}</a></li>`;
    return [
        `                <div class="footer-col">`,
        `                    <h3>${label}</h3>`,
        `                    <ul class="footer-links">`,
        link('chi-siamo.html', 'Chi Siamo'),
        link('contatti.html', 'Contatti'),
        link('privacy.html', 'Privacy Policy'),
        link('cookie-policy.html', 'Cookie Policy'),
        `                    </ul>`,
        `                </div>`,
        ``
    ].join(eol);
}

const socialCol = eol => [
    `                <div class="footer-col">`,
    `                    <h3>Seguici</h3>`,
    `                    <div class="social-links">`,
    `                        <a href="https://www.facebook.com/InfissiParadise/" target="_blank" aria-label="Facebook"><i class="ph ph-facebook-logo"></i></a>`,
    `                        <a href="https://www.instagram.com/infissiparadise/" target="_blank" aria-label="Instagram"><i class="ph ph-instagram-logo"></i></a>`,
    `                    </div>`,
    `                </div>`
].join(eol);

function processPage(filePath, prefix) {
    let c = fs.readFileSync(filePath, 'utf-8');
    const eol = detectEol(c);
    const infoCol = footerBlock(eol, prefix, 'Informazioni');

    // If already has Informazioni footer column, fix comments and return
    const infoCheck = prefix ? 'href="../privacy.html"' : 'href="privacy.html"';
    if (c.includes(infoCheck)) {
        // Remove stray <!-- Social --> comment that might sit above Informazioni
        const strayComment = '<!-- Social -->' + eol;
        const socialBlock = socialCol(eol);
        if (c.includes(strayComment + infoCol.trimStart() && c.includes(strayComment))) {
            c = c.split(strayComment).join('');
        }
        fs.writeFileSync(filePath, c, 'utf-8');
        return true;
    }

    const socialBlock = socialCol(eol);
    if (c.includes(socialBlock)) {
        // Remove any existing <!-- Social --> comment above target (cleaner output)
        const strayCommentRegex = new RegExp('\\s*<!-- Social -->' + eol.replace(/\r/g, '\\r'));
        c = c.replace(strayCommentRegex, eol);
        c = c.replace(socialBlock, infoCol + socialBlock);
        fs.writeFileSync(filePath, c, 'utf-8');
        return true;
    }
    return false;
}

let updated = 0;
rootFiles.forEach(f => {
    if (['privacy.html', 'cookie-policy.html', 'chi-siamo.html'].includes(f)) return;
    const filePath = path.join(rootDir, f);
    if (processPage(filePath, false)) { console.log('Updated ' + f); updated++; }
});

blogFiles.forEach(f => {
    const filePath = path.join(rootDir, f);
    if (processPage(filePath, true)) { console.log('Updated ' + f); updated++; }
});

console.log('Total updated:', updated);