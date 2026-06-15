NPM ?= npm

.DEFAULT_GOAL := help

.PHONY: help install serve build clean

help:
	@printf "\033[32m%-10s\033[0m %s\n" "install" "安装项目依赖"
	@printf "\033[32m%-10s\033[0m %s\n" "serve" "运行 GitBook 服务器"
	@printf "\033[32m%-10s\033[0m %s\n" "build" "构建 GitBook 静态页面"
	@printf "\033[32m%-10s\033[0m %s\n" "clean" "删除构建产物"

install:
	$(NPM) install

serve:
	$(NPM) run serve

build:
	$(NPM) run build

clean:
	rm -rf _book
