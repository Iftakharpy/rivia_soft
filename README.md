# RIVIAGW


## Prod commands
```bash
# optimize css for production
tailwind -c "tailwind.config.js" -i "static\css\tailwind.css" -o "static\css\style.css" --minify
```

## Dev env commands

```bash
# Navigate to project directory
cd path/to/proj/dir
# cd "C:\Users\iftak\Desktop\projects\riviagw\"

# Run django dev server
python ./manage.py runserver

# Watch and build tailwind classes
# use tailwind_cli v3.x.x for now, v4 has deprecated some utility classes
tailwind -c "tailwind.config.js" -i "static\css\tailwind.css" -o "static\css\style.css" -w
```
