const fs = require('fs');
const path = require('path');

const rootDir = __dirname + '/..';

// Pages to update: all root HTML files + blog articles
const rootFiles = fs.readdirSync(rootDir).filter(f => f.endsWith('.html'));
const blogDir = path.join(rootDir, 'blog');
const blogFiles = fs.readdirSync(blogDir).filter(f => f.endsWith('.html')).map(f => path.join('blog', f));

const files = {
    root: rootFiles.filter(f => f !== 'privacy.html' && f !== 'cookie-policy.html' && f !== 'chi-siamo.html'),
    blog: blogFiles
};

// Footer 'Informazioni' column for root pages
const infoColRoot = `                <div class="footer-col">
                    <h3>Informazioni</h3>
                    <ul class="footer-links">
                        <li><a href="chi-siamo.html">Chi Siamo</a></li>
                        <li><a href="contatti.html">Contatti</a></li>
                        <li><a href="privacy.html">Privacy Policy</a></li>
                        <li><a href="cookie-policy.html">Cookie Policy</a></li>
                    </ul>
                </div>

`;

// Footer 'Informazioni' column for blog pages (../ prefix)
const infoColBlog = `                <div class="footer-col">
                    <h3>Informazioni</h3>
                    <ul class="footer-links">
                        <li><a href="../chi-siamo.html">Chi Siamo</a></li>
                        <li><a href="../contatti.html">Contatti</a></li>
                        <li><a href="../privacy.html">Privacy Policy</a></li>
                        <li><a href="../cookie-policy.html">Cookie Policy</a></li>
                    </ul>
                </div>

`;

function getFooterSocialBlock(prefix) {
    if (prefix) {
        return `                <div class="footer-col">
                    <h3>Seguici</h3>
                    <div class="social-links">
                        <a href="https://www.facebook.com/InfissiParadise/" target="_blank" aria-label="Facebook"><i class="ph ph-facebook-logo"></i></a>
                        <a href="https://www.instagram.com/infissiparadise/" target="_blank" aria-label="Instagram"><i class="ph ph-instagram-logo"></i></a>
                    </div>
                </div>`;
    }
    return `                <div class="footer-col">
                    <h3>Seguici</h3>
                    <div class="social-links">
                        <a href="https://www.facebook.com/InfissiParadise/" target="_blank" aria-label="Facebook"><i class="ph ph-facebook-logo"></i></a>
                        <a href="https://www.instagram.com/infissiparadise/" target="_blank" aria-label="Instagram"><i class="ph ph-instagram-logo"></i></a>
                    </div>
                </div>`;
}

// Root pages
rootFiles.forEach(f => {
    const filePath = path.join(rootDir, f);
    let c = fs.readFileSync(filePath, 'utf-8');

    let changed = false;

    // 1. Add favicon after theme-color
    if (!c.includes('rel="shortcut icon"') && !c.includes('rel="icon"')) {
        c = c.replace(
            /(<meta name="theme-color" content="#4C8A71">)/,
            '$1\n    <link rel="shortcut icon" href="favicon.svg" type="image/svg+xml">'
        );
        changed = true;
    }

    // 2. Add Informazioni footer column before Seguici column (root pages)
    const socialBlock = getFooterSocialBlock(false);
    if (!c.includes('href="privacy.html"') && c.includes(socialBlock)) {
        c = c.replace(socialBlock, infoColRoot + socialBlock);
        changed = true;
    }

    if (changed) {
        fs.writeFileSync(filePath, c, 'utf-8');
        console.log(`Updated ${f}`);
    }
});

// Blog pages
blogFiles.forEach(f => {
    const filePath = path.join(rootDir, f);
    let c = fs.readFileSync(filePath, 'utf-8');

    let changed = false;

    // 1. Add favicon after theme-color with ../ prefix
    if (!c.includes('rel="shortcut icon"') && !c.includes('rel="icon"')) {
        c = c.replace(
            /(<meta name="theme-color" content="#4C8A71">)/,
            '$1\n    <link rel="shortcut icon" href="../favicon.svg" type="image/svg+xml">'
        );
        changed = true;
    }

    // 2. Add Informazioni footer column before Seguici column (blog pages)
    const socialBlock = getFooterSocialBlock(true);
    if (!c.includes('href="../privacy.html"') && c.includes(socialBlock)) {
        c = c.replace(socialBlock, infoColBlog + socialBlock);
        changed = true;
    }

    if (changed) {
        fs.writeFileSync(filePath, c, 'utf-8');
        console.log(`Updated ${f}`);
    }
});

// cosmeton: also add favicon to privacy/cookie/chi-siamo already done manually? check
['privacy.html', 'cookie-policy.html', 'chi-siamo.html'].forEach(f => {
    const filePath = path.join(rootDir, f);
    let c = fs.readFileSync(filePath, 'utf-8');
    if (!c.includes('rel="shortcut icon"')) {
        c = c.replace(
            /(<meta name="theme-color" content="#4C8A71">)/,
            '$1\n    <link rel="shortcut icon" href="favicon.svg" type="image/svg+xml">'
        );
        fs.writeFileSync(filePath, c, 'utf-8');
        console.log(`Updated favicon in ${f}`);
    }
});

console.log('Done.');