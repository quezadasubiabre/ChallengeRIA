# ChallengeRIA

# DEChallenge

1. crear imagen container:
```
$ docker build -t api_signal:v1 .

```
2. run container

```
$ docker run -dit --rm -p 5000:5000 --name api_signal api_signal:v1

```

3. url API


```
http://localhost:5000/signal

```
