"use client";
import React from "react";
import { ChevronRight, Router } from "lucide-react";
import { Accordion } from "@/components/Accordion";
import { useRouter } from "next/navigation";
import { Footer } from "@/components/Footer";

export default function RiceFarmingPage() {
  const router = useRouter();
  return (
    <div className="min-h-screen bg-white font-sans">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-white p-4 border-b">
        <div className="flex items-center justify-between">
          <span className="text-sm">Rice maid</span>
          <span className="bg-yellow-400 text-xs px-2 py-1 rounded-full">
            FAQ
          </span>
        </div>
      </header>

      {/* Main Content */}
      <main className="p-6 space-y-6">
        {/* Hero Section */}
        <section className="space-y-2 gap-2 flex flex-col justify-center items-center">
          <>
            <h1 className="text-[32px] font-bold">Rice Farming</h1>
            <h1 className="text-[32px] font-bold">Essentials</h1>
          </>
          <>
            <p className="text-[20px] text-gray-600">
              Discover the Secrets to Successful
            </p>
            <p className="text-[20px] text-gray-600">Rice Cultivation</p>
          </>
          <button onClick={() => router.push("https://www.ricethailand.go.th/")} className="w-full bg-[#FFD903] h-[44px] rounded-[22px] text-[#51470D] font-bold">
            Learnmore
          </button>
        </section>

        <section className="space-y-2 gap-2 flex flex-col justify-center items-center">
          <>
            <h1 className="text-[32px] font-bold">Mastering Rice</h1>
            <h1 className="text-[32px] font-bold">Farming Techniques</h1>
          </>
          <>
            <p className="text-[20px] text-gray-600">
              Optimize Your Yield: Essential
            </p>
            <p className="text-[20px] text-gray-600">
              Insights for Rice Growers
            </p>
          </>
        </section>

        {/* Image */}
        <div className="relative">
          <img
            src="/images/Container 6_Mobile.png"
            alt="Rice Field"
            className="w-full object-cover rounded-lg"
          />
        </div>

        {/* Nested Accordion for Sections */}
        <section className="space-y-4">
          <Accordion title="Soil Preparation">
            <Accordion title="Ploughing the Paddy Field">
              Ploughing the paddy field is the first plowing along the length of
              the paddy field.
            </Accordion>
            <Accordion title="Transforming the Soil">
              After the soil has been dried for a while, transforming the soil
              will help turn the buried soil again.
            </Accordion>
            <Accordion title="Harrowing">
              To remove weeds from the paddy field and break the soil down into
              smaller pieces.
            </Accordion>
          </Accordion>

          <Accordion title="Planting">
            <Accordion title="Seeding">
              Seeding is used for upland rice planting on hillsides or in high
              areas. Planting method: After preparing the soil, dig a hole or
              make a furrow, then drop the seeds into the hole or furrow, then
              cover the hole or furrow.
            </Accordion>
            <Accordion title="Broadcasting">
              Broadcasting is done in areas where water control is difficult.
              There are 2 methods for sowing: dry sowing or germinated rice
              sowing.
            </Accordion>
          </Accordion>

          <Accordion title="Harvesting">
            <Accordion title="Steps">
              After the rice flowers or ears are about 20 days old, farmers will
              drain the water quickly to speed up the maturation of the rice and
              to prevent the seeds from being too moist.
            </Accordion>
          </Accordion>

          <Accordion title="Rice Threshing">
            <Accordion title="Steps">
              After drying the rice, farmers transport it to the threshing floor
              and then thresh the rice grains from the stalks. In some places,
              people use human labor, while in some places, buffaloes or cows
              trample the rice. However, rice threshing machines are now used.
            </Accordion>
          </Accordion>
        </section>

        <div className="relative flex flex-row item-center gap-4">
          <img
            src="/images/kaologo-1.png"
            alt="Rice Field"
            className="w-[74px] h-[74px] object-cover rounded-lg"
          />
          <div className="text-[24px]">
            How to prevent and eliminate pests in rice fields
          </div>
        </div>

        <div className="relative flex flex-row item-center gap-4">
          <img
            src="/images/mang.jpg"
            alt="Rice Field"
            className="object-cover rounded-[22px]"
          />
        </div>
        <div className="relative flex">
          Observe the rice fields in detail regularly. Get rid of weeds around
          the rice fields to prevent insects from hiding.
        </div>
        <div className="relative flex flex-row item-center gap-4">
          <img
            src="/images/techno.jpeg"
            alt="Rice Field"
            className="object-cover rounded-[22px]"
          />
        </div>
        <div className="relative flex">
          1. Land leveling using laser land leveling machinery is the use of
          machinery to prepare the soil, which is controlled by a laser light
          system.
        </div>
        <div className="relative flex">
          2. Rice planting using a rice planting car with a driverless steering
          wheel is a rice planting car using an automatic steering wheel to
          control the direction with a GPS system so that the rows of rice are
          straight. It is a convenient method and can reduce costs by more than
          20%.
        </div>
        <div className="relative flex">
          3. Sowing rice with agricultural drones is a method of sowing rice
          that provides uniformity, reducing labor, working time and reducing
          seed rate.
        </div>

        <div className="relative flex flex-row item-center gap-4">
          <img
            src="/images/kaologo2.png"
            alt="Rice Field"
            className="w-[74px] h-[74px] object-cover rounded-lg"
          />
          <div>
            <div className="text-[24px]">Environment Information</div>
            <div className="text-[24px]">Water and Weather</div>
          </div>
        </div>

        {/* Content Cards */}
        <div className="space-y-4">
          <div className="p-4 space-y-2">
            <h2 className="text-lg font-semibold">Thai water level</h2>
            <p className="text-sm text-gray-600">
              View the water resouce and rain level in Thailand
            </p>
            <button
              onClick={() => router.push("/water")}
              className="text-yellow-600 text-sm font-semibold flex items-center"
            >
              Learn more <ChevronRight className="h-4 w-4 ml-1" />
            </button>
          </div>

          <div className="p-4 space-y-2">
            <h2 className="text-lg font-semibold">Weather Forecast</h2>
            <p className="text-sm text-gray-600">
              Get the latest weather forecast for your region
            </p>
            <button
              onClick={() => router.push("/weather")}
              className="text-yellow-600 text-sm font-semibold flex items-center"
            >
              Learn more <ChevronRight className="h-4 w-4 ml-1" />
            </button>
          </div>

          <div className="p-4 space-y-2">
            <h2 className="text-lg font-semibold">
              Carbon Credit Calculator for Rice Farmers
            </h2>
            <p className="text-sm text-gray-600">
              Get the documentation and support you need to calculate your
              carbon
            </p>
            <button
              onClick={() => router.push("/cc")}
              className="text-yellow-600 text-sm font-semibold flex items-center"
            >
              Learn more <ChevronRight className="h-4 w-4 ml-1" />
            </button>
          </div>

          <div className="relative py-8">
            <div className="bg-yellow-50 p-4 space-y-2">
              <h2 className="text-lg font-semibold">
                Adapting to Climate Rice Farming in the 21st Century
              </h2>
              <p className="text-sm text-gray-600">
                Embracing Innovation Technology and Techniques Shaping the
                Future
              </p>
            </div>
            {/* Decorative Image */}
            <div className="absolute bottom-0 right-0 transform translate-y-1/2">
              <div className="w-24 h-24 bg-yellow-400 rounded-tl-3xl"></div>
            </div>
          </div>
        </div>
        <Footer />
      </main>
    </div>
  );
}
