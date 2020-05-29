import inspect

class User():
    def __init__(self, name, login):
        self.name = name
        self.login = login

    def user_random(self, name, login):
        self.__init__(name+'rand', login+'rand')

    def __str__(self):
        return f"{self.name} {self.login}"


if __name__ == "__main__":
    user1 = User('name', 'login')
    print(user1)
    user1.user_random('name1','login1')
    print(user1)

