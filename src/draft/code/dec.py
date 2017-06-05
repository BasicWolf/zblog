#-- 1
def walk(speed):
    print('Now walking! Speed: {}'.format(speed))

# walk(10)
# >>> Now walking! Speed: 10

def walk(speed):
    
    print('Now walking! Speed: {}'.format(speed))


#-- 2
def limit_speed(self, f):
    def wrapped(speed):
        if speed > 1:
            speed = 1
        return f(speed)
    return wrapped

#-- 3
run_with_limit = limit_speed(run)
walk_with_limit = limit_speed(walk)

# run_with_limit(10)
# >>>

#-- 4
@limit_speed
def run(speed):
    print('Now running! Speed: {}'.format(speed))
