# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: dcyprien <dcyprien@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2022/09/28 10:56:09 by minh-ngu          #+#    #+#              #
#    Updated: 2024/04/15 13:09:28 by dcyprien         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

all:
	@docker compose -f ./docker-compose.yml up -d --build
	@docker compose -f ./docker-compose.yml logs -f

down:
	@docker compose -f ./docker-compose.yml down

up:
	@docker compose -f ./docker-compose.yml up -d --build
	@docker compose -f ./docker-compose.yml logs -f

stop:
	@docker stop $$(docker ps)

remove_con:
	@docker rm -f $$(docker ps -a -q)

remove_images:
	@docker image prune --all --force

re:
	@make down
	@make up

clean:
	-docker exec -it blockchain rm -rf app/blockchain/build
	-docker stop $$(docker ps -qa)
	-docker rm $$(docker ps -qa)
	-docker rmi -f $$(docker images -qa)
	-docker volume rm $$(docker volume ls -q)
	-docker network rm $$(docker network ls -q)
	gio trash -f backend/game/migrations/[!__init__.py]*
	gio trash -f backend/accounts/migrations/[!__init__.py]*
	gio trash -f backend/pong/migrations/[!__init__.py]*
	gio trash -f backend/transchat/migrations/[!__init__.py]*

	
# gitf: git in final
# gitd: git in developpement
# Ex: make gitd M="your message"


#flush database : 
#docker exec -it django python3 /app/backend/manage.py flush

CLI:
	pip3 install --user keyboard --break-system-packages
	pip3 install --user websockets --break-system-packages
	clear && cd backend/CLI && sudo python3 CLI.py 127.0.0.1 8080
	#clear && cd backend/CLI && valgrind --leak-check=full python3 CLI.py
	#cd backend/CLI && node CLI.js

M:=
test:
	cd backend && python3 manage.py runserver 0.0.0.0:8000	
gitf:
	make clean
	git add Makefile
	git add backend/*
	git add frontend/*
	git commit -m "all"
	git push
gitd:
	make gitclean
	git add -A -- :!*.o :!*.swp :!*.env :!*.crt :!*.key
	git commit -m "$(M)"
	git push
gitclean:
	# Clean migration folder
	gio trash -f backend/game/migrations/[!__init__.py]*
	gio trash -f backend/db.sqlite3
	# Clean __pycache__
	find . -type d -name "__pycache__" -exec gio trash -f {} +

migrate:
	$(shell cd backend && python3 manage.py makemigrations)
	$(shell cd backend && python3 manage.py migrate)
	
.PHONY: all clean fclean re test



# *********** OLD MAKEFILE WITHOUT DOCKER TO EXECUTE LOCALLY *******************


# M:=
# test:
# 	cd backend && python3 manage.py runserver 0.0.0.0:8000	
# gitf:
# 	make clean
# 	git add Makefile
# 	git add backend/*
# 	git add frontend/*
# 	git commit -m "all"
# 	git push
# gitd:
# 	make clean
# 	git add -A -- :!*.o :!*.swp
# 	git commit -m "$(M)"
# 	git push
# clean:
# 	# Clean migration folder
# 	gio trash -f backend/game/migrations/[!__init__.py]*
# 	#$(shell cd backend && python3 manage.py migrate)
# 	#$(shell cd backend && python3 manage.py makemigrations)
# 	#$(shell cd backend && python3 manage.py migrate)
# 	# Clean __pycache__
# 	find . -type d -name "__pycache__" -exec gio trash -f {} +

# .PHONY: all clean fclean re test
