const fs = require('fs');
const path = require('path');

const dir = __dirname;
const files = fs.readdirSync(dir).filter(f => f.endsWith('.html'));

const themeColorMeta = '<meta name="theme-color" content="#4C8A71">';
const preconnectUnsplash = '<link rel="preconnect" href="https://images.unsplash.com">';

files.forEach(file => {
    let content = fs.readFileSync(path.join(dir, file), 'utf-8');

    // 1. Add theme-color meta tag if not exists
    if (!content.includes('name="theme-color"')) {
        content = content.replace(/(<meta name="viewport"[^>]*>)/i, '$1\n    ' + themeColorMeta);
    }

    // 2. Add preconnect to unsplash if not exists
    if (!content.includes('href="https://images.unsplash.com"')) {
        content = content.replace(/(<link rel="preconnect" href="https:\/\/fonts\.gstatic\.com" crossorigin>)/i, '$1\n    ' + preconnectUnsplash);
    }

    // 3. Add loading="lazy" and decoding="async" to images (except those with class="logo-img" or inside hero)
    content = content.replace(/<img\s([^>]+)>/gi, (match, attrs) => {
        if (attrs.includes('loading=') || attrs.includes('decoding=')) {
            return match; // already has it
        }
        if (attrs.includes('class="logo-img"')) {
            return match; // don't lazy load logo
        }
        // If it's the hero image in index.html, we shouldn't lazy load it. But wait, index.html hero is a video or background.
        return `<img ${attrs} loading="lazy" decoding="async">`;
    });

    // 4. Correggere .badge-light nelle hero bianche (badge ora scuro) -> rimuovere 'badge-light' e mettere magari 'badge-dark' o solo 'badge'
    // Actually, let's just replace 'badge-light' with 'badge' in the specific hero sections if any.
    // The classes used might be "badge badge-light".
    // "grate-sicurezza.html", "tende-da-sole.html", "persiane.html", "finestre.html"
    // Let's just remove badge-light globally and replace with a standard badge style or badge-primary.
    // Wait, let's look at the html.
    content = content.replace(/class="badge badge-light"/g, 'class="badge badge-primary"');
    content = content.replace(/class="badge-light"/g, 'class="badge-primary"');

    fs.writeFileSync(path.join(dir, file), content, 'utf-8');
    console.log(`Updated ${file}`);
});
