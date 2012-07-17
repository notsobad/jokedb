db.jokes.find().forEach(function(j){
	j.r = Math.random();
	db.jokes.save(j);
});
