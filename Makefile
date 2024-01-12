# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    Makefile                                           :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: minh-ngu <marvin@42.fr>                    +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2022/09/28 10:56:09 by minh-ngu          #+#    #+#              #
#    Updated: 2024/01/12 06:57:44 by ngoc             ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

test:
	cd backend && python3 manage.py runserver 0.0.0.0:8000	
gits:
	git add Makefile
	git add backend/*
	git add frontend/*
	git add api/*
	git commit -m "all"
	git push
.PHONY: all clean fclean re test
