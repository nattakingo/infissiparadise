const fs = require('fs');
['avvolgibili.html','grate-sicurezza.html','tende-da-sole.html'].forEach(f => {
    let c = fs.readFileSync(f, 'utf-8');
    c = c.replace(/class="product-split-section/g, 'class="product-detail-split');
    fs.writeFileSync(f, c);
    console.log('Updated ' + f);
});
