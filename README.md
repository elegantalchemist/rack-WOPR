# rack_WOPR

A fast and cheap project to make a 1U rack filler with a WOPR-inspired blinking lights effect. Now your favourite psychopathic supercomputer can live with you every day!

![Gif of WOPR running](https://github.com/elegantalchemist/rack-WOPR/blob/main/photos/WOPR-gifs.gif?raw=true)

A video of it running on the bench

## Materials
* **Dot matrix LED Module** - These are super basic 8x8 modules sometimes referred to as MAX7219 modules. You can buy them on single control boards or you can buy them in pre-made racks of 4 modules. I used these ones from Amazon UK in packs of 2  - https://www.amazon.co.uk/dp/B07YWRZ3FC but you can also find them on Amazon US like this https://www.amazon.com/dp/B07FFV537V - either way it's about £6/$8 for each rack of 4. You'll find that 3 in a row fits in 1U rack just right. They link together in series and can easily be soldered one to another to make a single rack of 96x8 LEDs.
* **Arduino Uno** - primary controller for the code and signalling. You only need a very basic single microcontroller board and other boards like a RasPi Pico (different code needed) or a Arduino Nano will work just fine. No need for any networking, wifi etc etc, just the most basic IO board. About £10/$12 here.
* **A rack mount or case** - I used this 3D print model https://www.printables.com/model/1231389-1u-wopr made by printables user [@Seth_215443](https://www.printables.com/@Seth_215443)
* **(Optional) - Cheap case** You could instead take a cheap 1U metal rack blank (<£5) and either fix to the front with hot glue, or add perspex etc around the outside. Something like this: https://www.amazon.co.uk/dp/B01MFA1QBK

## Building this Hardware


## Building this software

## Credits
Full credit to u/aforsberg who made v1 of this project. The main changes here are about the code being in Arduino format and having added a lot of flexibility - my code lets you change speed, percentage of LEDs lit, percentage of rows changing each time etc.
His project can be seen here: https://www.reddit.com/r/homelab/comments/1iboomc/i_spent_a_few_days_designing_a_1u_bar_of_leds/

Credit also to harddal @ github who initially provided arduino code conversion: https://github.com/harddal/WOPR-LED/tree/main
