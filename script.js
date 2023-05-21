let value = prompt("Input something:");
let res = value;
alert(res);
let a, b = 20, c = "Hello, world!";
switch(b){
    case 1:
        a = "One";
        break;
    case 2:
        a = "Two";
        break;
    default:
        a = "Number";
        break;
}
if(c == "Hello, world"){
    if(a == "One" && c == "Hello, world"){
        alert("Good result");
    }
} else{
    let num = 90;
    num += 5;
    alert (num);
}
for(let i = 0; i < 12; i++){
    let j = i;
    while(j > 0){
        alert((i + j)*(5 + 3*(9 + 7)) % j);
        if(j == 9)
            break;
    }
    let k = i ^ j;
    do{
        k += 1;
        alert("Do while...");
    }while(k < 8)
}
let initValue = 111;
let sum = 0;
for (let m = 1; m < 45; m++) {
    let tempValue = m * initValue % (m + initValue) / (m + 5) + 15;
    sum += tempValue;
}
alert(sum);
if (sum > 45) {
    sum -= 5;
    alert(sum);
} else if (sum > 30) {
    sum *= 1.5;
    sum += 33;
    alert(sum);
} else {
    sum ^= 3;
    sum /= 1.5;
    alert(sum);
}
user_answer = prompt("Do you want to end?(Y/N): ")
if (user_answer === "Y") {
    alert("The end...");
} else if (user_answer === "N") {
    alert("But program want to rest....");
    alert("Goodbye my boy");
} else {
    let errorMessage = "Bro, you typed incorrect character, please look more carefully on rules)!";
    alert(errorMessage);
}
let result = 0;
alert("True end");
