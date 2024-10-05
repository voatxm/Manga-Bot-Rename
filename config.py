env_vars = {
  # Get From my.telegram.org
  "API_HASH": "3257596471c6d08212b3c0a47cc815ea",
  # Get From my.telegram.org
  "API_ID": "23578854",
  #Get For @BotFather
  "BOT_TOKEN": "",
  # Get For tembo.io
  "DATABASE_URL_PRIMARY": "postgresql://postgres:tTvmOOxCA4TBnFOR@ashamedly-large-feline.data-1.use1.tembo.io:5432/postgres",
  # Logs Channel Username Without @
  "CACHE_CHANNEL": "-1002198538597",
  # Force Subs Channel username without @
  "CHANNEL": "Manga_Yugen",
  # {chap_num}: Chapter Number
  # {chap_name} : Manga Name
  # Ex : Chapter {chap_num} {chap_name} @Manhwa_Arena
  "FNAME": "[MY] [{chap_num}] {chap_name} @Manga_Yugen"
}

dbname = env_vars.get('DATABASE_URL_PRIMARY') or env_vars.get('DATABASE_URL') or 'sqlite:///test.db'

if dbname.startswith('postgres://'):
    dbname = dbname.replace('postgres://', 'postgresql://', 1)
    
