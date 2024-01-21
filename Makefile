# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: minh-ngu <marvin@42.fr>                    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2022/09/28 10:56:09 by minh-ngu          #+#    #+#              #
#    Updated: 2024/01/19 07:05:15 by ngoc             ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

all:
	@sudo docker compose -f ./docker-compose.yml up -d --build

down:
	@sudo docker compose -f ./docker-compose.yml down

up:
	@sudo docker compose -f ./docker-compose.yml up -d --build

stop:
	@sudo docker stop $$(sudo docker ps)

remove_con:
	@sudo docker rm -f $$(sudo docker ps -a -q)

remove_images:
	@sudo docker image prune --all --force

re:
	@make down
	@make up

clean:
	@sudo docker stop $$(docker ps -qa);\
	sudo docker rm $$(docker ps -qa);\
	sudo docker rmi -f $$(docker images -qa);\
	sudo docker volume rm $$(docker volume ls -q);\
	sudo docker network rm $$(docker network ls -q);\
	
# gitf: git in final
# gitd: git in developpement
# Ex: make gitd M="your message"

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
	git add -A -- :!*.o :!*.swp
	git commit -m "$(M)"
	git push
gitclean:
	# Clean migration folder
	gio trash -f backend/game/migrations/[!__init__.py]*
	# Clean __pycache__
	find . -type d -name "__pycache__" -exec gio trash -f {} +

migrate:
	$(shell cd backend && python3 manage.py makemigrations)
	$(shell cd backend && python3 manage.py migrate)
	
.PHONY: all clean fclean re test
