## YPC_TELEGRAM_BOT

### setup
- install requirements
```bash
pip3 install -r requirements.txt
```
- config
```bash
cp telezombie.example.yaml telezombie.yaml
# edit YOUR_TELEGRAM_BOT_API_TOKEN in telezombie.yaml
```
- execute database migration (sqlite3)
```bash
env DATABASE_URL='sqlite:///database.db' ./alembic.sh upgrade head
```
- start app
```bash
python3 -m bot --config=./telezombie.yaml
```