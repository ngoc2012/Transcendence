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
	make clean
	git add -A -- :!*.o :!*.swp
	git commit -m "$(M)"
	git push
clean:
	# Clean migration folder
	gio trash -f backend/game/migrations/[!__init__.py]*
	#$(shell cd backend && python3 manage.py migrate)
	#$(shell cd backend && python3 manage.py makemigrations)
	#$(shell cd backend && python3 manage.py migrate)
	# Clean __pycache__
	find . -type d -name "__pycache__" -exec gio trash -f {} +

.PHONY: all clean fclean re test
