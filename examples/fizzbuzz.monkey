let fizzbuz = fn(x) {
     if (x % 15 == 0) { "Fizzbuzz"; }
     else if (x % 5 == 0) { "Buzz"; }
     else if (x % 3 == 0) { "Fizz"; }
     else { x; };
};

let rec_fizz = fn(x) {
    if (x == 0) { }
    else { 
        puts(fizzbuz(x));
        rec_fizz(x-1);
    };
};

let while_fizz = fn(x) {
    let y = 1;
    while (y <= x) {
        puts(fizzbuz(y));
        y = y + 1;
    };
};

while_fizz(16);
//rec_fizz(20);