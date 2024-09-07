let counter = fn() {
  let x = 0;
  fn() {
    let y = x;
    x = x + 1;
    y;
  };
};

let x = counter();
//puts(x());
//puts(x());
//puts(x());
//puts(x());
//puts(x());