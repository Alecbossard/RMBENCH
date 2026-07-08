cd assets
python _download.py

cd ..

echo "Configuring Path ..."
if [ -f ./script/setup_svlr_assets.py ]; then
  python ./script/setup_svlr_assets.py
else
  python ./script/update_embodiment_config_path.py
fi
