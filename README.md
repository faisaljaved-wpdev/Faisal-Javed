Faisal Javed Portfolio <br>
This repository hosts the portfolio website faisaljaved.pro. It includes a sitemap generator that automatically creates and updates sitemaps using GitHub Actions.<br>

Sitemap Generator Setup<br>
1. Files:<br>
▶ generate_sitemap.py: Generates sitemaps (root folder).<br>
▶ robots.txt: Defines sitemap URL (root folder).<br>
▶ .github/workflows/sitemap.yml: Automates sitemap generation.<br>

2. GitHub Actions:<br>
▶ Go to Actions tab and enable workflows.<br>
▶ Run the "Generate and Deploy Sitemap" workflow manually first.<br>

3. Generated Sitemaps:<br>
▶ Check /sitemap/ folder for:<br>
   ▶ sitemap_index.xml<br>
   ▶ sitemap-pages.xml<br>
   ▶ sitemap-images.xml<br>
   ▶ sitemap-videos.xml<br>
   ▶ sitemap-pdfs.xml<br>
▶ Visit https://faisaljaved.pro/sitemap.xml.<br>

4. Google Search Console:<br>
▶  Submit https://faisaljaved.pro/sitemap.xml in Sitemaps section.<br>



Notes<br>
▶ Sitemap auto-updates on every push.<br>
▶ Dependencies (requests, beautifulsoup4, lxml) are handled by GitHub Actions.<br>

