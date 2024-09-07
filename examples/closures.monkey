let x = 0;
let f = fn() { x = x + 1; x;};
let g = fn() { x = x + 1; x;};

puts(f());
puts(g()); 