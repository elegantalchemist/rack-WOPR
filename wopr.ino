//A simple, easily modified ARDUINO script to display a WOPR style light panel on a series of 8x8 LED panels,
//contains easily changed settings for speed, percentage chance of a column changing and rough percentage of 
// total pixels lit. 

//CREDITS
//Original project by u/aforsberg on reddit
//https://www.reddit.com/r/homelab/comments/1iboomc/i_spent_a_few_days_designing_a_1u_bar_of_leds/

//Original arduino code conversion by harddal @ github
//https://github.com/harddal/WOPR-LED/tree/main

#include <MD_Parola.h>
#include <MD_MAX72xx.h>
#include <SPI.h>

// Wiring
// CS to pin 3
// DIN to pin 11
// CLK to pin 13

#define HARDWARE_TYPE MD_MAX72XX::FC16_HW

#define DEVICES 12
#define CS_PIN 3

MD_Parola display = MD_Parola(HARDWARE_TYPE, CS_PIN, DEVICES);

void setup() 
{
  Serial.begin(9600);

  randomSeed(analogRead(0));

	display.begin();

	display.setIntensity(2);

	display.displayClear();
}

void loop() 
{
  for (int r = 0; r < 8; r++)
  {
    for (int c = 0; c < 96; c++)
    {
        int flip1 = random(0, 5);   //what chance of that column changing at all - between 0 and 5 so chance 0 = 20%
                                    //use a smaller range to have the panel look more 'active' and lower to be a slower crawl

        if (flip1 == 0)
        {
           int flip2 = random(0, 10); //what percentage probability of 8 lights in that column being lit - total percentage lit

              if ((flip2 >=0) && (flip2<=4)) //picks yes for 0 to 4 out of 10, so about 40% lit. Larger range = more 'full' looking panel, etc
              {
                display.getGraphicObject()->setPoint(r, c, true);
              }          
          else
          {
            display.getGraphicObject()->setPoint(r, c, false);
          }
        }
    }
}




//Timing Transitions Speed
//set whatever times you feel like for slower/faster transitions
//250-500-750 is fairly fast, you can try 500-1000-1500 for slower times or 
//even something like 250-500-3000 if you want highly unpredictable/variable
//timings or could change to 250-250-250 (or similar) for no variability

  int time = random(0, 3); 
  if (time == 0)
  {
      delay(250);
  }
  else if (time == 1)
  {
      delay(500);
  }
  else if (time == 2)
  {
      delay(750);
  }
}
