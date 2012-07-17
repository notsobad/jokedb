
db.jokes.find().forEach(function(joke){
	joke.random = Math.random();
	db.jokes.save(joke);
});
