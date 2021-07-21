if [ ! -d "./migrations" ]; 
then
    flask db init
else
    echo "migrations is exists"
fi
flask db migrate -m "update"&&flask db upgrade