# Real refXAS VM Test Commands

## 1. Local syntax check

```powershell
cd <Real_refXAS folder>
python -m py_compile auto_dataset_create.py plugins/read_data.py quality_control/quality_check.py auto_bl_create.py xafsdb_web/views.py xafsdb_web/urls.py xafsdb_web/utils.py webserver/settings.py webserver/urls.py
```

## 2. Start stack

```powershell
cd xafsdb_deployment
copy .env.example .env
# edit .env with real secrets before production

docker compose config
docker compose up -d
docker compose logs -f xafsdb
```

## 3. Quick checks

```powershell
docker compose ps
curl http://localhost/
curl http://localhost/dataset/list
```

## 4. Upload tests

Test in this order:

1. `.xdi`
2. `.dat`
3. `.spec`
4. `.h5` or `.hdf5`
5. `.nxs`

Expected flow:

Upload → Verify page with extracted metadata → Submit → QC runs → SciCat dataset created → curator email attempted → dataset visible in list → curator approval page works → dataset ZIP export works.

## 5. MongoDB/SciCat checks

```powershell
docker compose exec mongodb mongo --eval "show dbs"
docker compose logs scicat --tail=100
```

If the Mongo shell is `mongosh` instead of `mongo`:

```powershell
docker compose exec mongodb mongosh --eval "show dbs"
```

## 6. Important safety check before KIT VM

Do not commit `.env`. Use `.env.example` only.
