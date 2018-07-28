help:
	@echo "\033[32minit\033[0m"
	@echo "    初始化GitBook"
	@echo "\033[32mrun\033[0m"
	@echo "    运行GitBook服务器"
	@echo "\033[32mbuild\033[0m"
	@echo "    构建GitBook静态页面"

init:
	sudo npm i -g gitbook-cli
	gitbook install

run:
	gitbook serve

build:
	gitbook build
