$products = @{
    "pvc.jpg" = "https://source.unsplash.com/featured/?windows,modern/400x300"
    "alu.jpg" = "https://source.unsplash.com/featured/?aluminum,frames/400x300"
    "grate.jpg" = "https://source.unsplash.com/featured/?security,grates/400x300"
    "zanzariere.jpg" = "https://source.unsplash.com/featured/?screen,insect/400x300"
    "tende.jpg" = "https://source.unsplash.com/featured/?blinds,sun/400x300"
    "porte.jpg" = "https://source.unsplash.com/featured/?security,door/400x300"
}

foreach ($key in $products.Keys) {
    try {
        echo "Downloading $key..."
        Invoke-WebRequest -Uri $products[$key] -OutFile "public/images/$key"
    } catch {
        echo "Unsplash failed for $key, trying Picsum..."
        Invoke-WebRequest -Uri "https://picsum.photos/400/300" -OutFile "public/images/$key"
    }
}

for ($i=1; $i -le 10; $i++) {
    try {
        echo "Downloading gallery-$i.jpg..."
        Invoke-WebRequest -Uri "https://source.unsplash.com/featured/?home,renovation/400x300" -OutFile "public/images/gallery-$i.jpg"
    } catch {
        echo "Unsplash failed for gallery-$i, trying Picsum..."
        Invoke-WebRequest -Uri "https://picsum.photos/400/300" -OutFile "public/images/gallery-$i.jpg"
    }
}
